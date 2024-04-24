from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator, BigQueryCreateEmptyDatasetOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

# Constants
PROJECT_ID = 'airflow-composer-transform-csv'
BUCKET_NAME = 'gcs-viseo-data-academy-22024-1'
FOLDER_NAME = 'DATA/in'
DATASET_NAME = 'raw'
TABLE_PREFIX = 'RAW_SALES_TABLE'
CSV_SOURCE = f'gs://{BUCKET_NAME}/{FOLDER_NAME}/*.csv'

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'catchup': False
}

# Define the DAG
with DAG(
    'data_extraction_and_loading_dag',
    default_args=default_args,
    description='DAG for extracting data from CSV files and loading into BigQuery',
    schedule_interval='0 10 * * *',  # Trigger daily at 10 AM UTC
) as dag:

    create_dataset_task = BigQueryCreateEmptyDatasetOperator(
        task_id='create_dataset',
        dataset_id=DATASET_NAME,
        project_id=PROJECT_ID,
        location='europe-west3',  # Correct location for the dataset
        exists_ok=True  # This avoids failing if the dataset already exists
    )

    create_bq_table_task = BigQueryCreateEmptyTableOperator(
        task_id='create_bq_table',
        dataset_id=DATASET_NAME,
        table_id=TABLE_PREFIX,
        schema_fields=[
            {'name': 'SaleID', 'type': 'STRING'},
            {'name': 'ProductID', 'type': 'STRING'},
            {'name': 'Quantity', 'type': 'STRING'},
            {'name': 'Price', 'type': 'STRING'},
            {'name': 'SaleDate', 'type': 'STRING'}
        ],
        project_id=PROJECT_ID,
        location='europe-west3'
    )

    load_to_bq_task = GCSToBigQueryOperator(
        task_id='load_to_bigquery',
        bucket=BUCKET_NAME,
        source_objects=[f'{FOLDER_NAME}/*.csv'],
        destination_project_dataset_table=f'{DATASET_NAME}.{TABLE_PREFIX}',
        source_format='CSV',
        write_disposition='WRITE_TRUNCATE',
        autodetect=False
    )

    # Define task dependencies
    create_dataset_task >> create_bq_table_task >> load_to_bq_task
