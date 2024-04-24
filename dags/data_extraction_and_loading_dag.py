from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyTableOperator,
    BigQueryCreateEmptyDatasetOperator,
)
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator


# Constants
PROJECT_ID = "airflow-composer-transform-csv"
BUCKET_NAME = "gcs-viseo-data-academy-22024-1"
FOLDER_NAME = "data"
DATASET_NAME = "raw"
LOCATION = "europe-west3"
TABLE_PREFIX = "RAW_SALES_TABLE"
CSV_SOURCE = f"gs://{BUCKET_NAME}/{FOLDER_NAME}/in/*.csv"
source_path = f"gs://{BUCKET_NAME}/{FOLDER_NAME}/in/"
archive_path = f"gs://{BUCKET_NAME}/{FOLDER_NAME}/archive/"
error_path = f"gs://{BUCKET_NAME}/{FOLDER_NAME}/error/"


# Define default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
    "catchup": False,
}

# Define the DAG
with DAG(
    "data_extraction_and_loading_dag",
    default_args=default_args,
    description="DAG for extracting data from CSV files and loading into BigQuery",
    schedule_interval="0 10 * * *",  # Trigger daily at 10 AM UTC
) as dag:

    create_dataset_task = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset",
        dataset_id=DATASET_NAME,
        project_id=PROJECT_ID,
        location=LOCATION,
        exists_ok=True,  # This avoids failing if the dataset already exists
    )

    create_bq_table_task = BigQueryCreateEmptyTableOperator(
        task_id="create_bq_table",
        dataset_id=DATASET_NAME,
        table_id=TABLE_PREFIX,
        schema_fields=[
            {"name": "SaleID", "type": "STRING"},
            {"name": "ProductID", "type": "STRING"},
            {"name": "Quantity", "type": "STRING"},
            {"name": "Price", "type": "STRING"},
            {"name": "SaleDate", "type": "STRING"},
        ],
        project_id="airflow-composer-transform-csv",
    )

    load_to_bq_task = GCSToBigQueryOperator(
        task_id="load_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=[f"{FOLDER_NAME}/*.csv"],
        destination_project_dataset_table=f"{DATASET_NAME}.{TABLE_PREFIX}",
        source_format="CSV",
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {"name": "SaleID", "type": "STRING", "mode": "NULLABLE"},
            {"name": "ProductID", "type": "STRING", "mode": "NULLABLE"},
            {"name": "Quantity", "type": "STRING", "mode": "NULLABLE"},
            {"name": "Price", "type": "STRING", "mode": "NULLABLE"},
            {"name": "SaleDate", "type": "STRING", "mode": "NULLABLE"},
        ],
        skip_leading_rows=1,  # Skip the first row (header)
        autodetect=False,  # Explicit schema provided, so autodetect is not needed
        field_delimiter=",",  # Assuming CSV delimiter is comma
        encoding="UTF-8",
    )

    # Move file to archive on success
    move_file_to_archive = GCSToGCSOperator(
        task_id="move_file_to_archive",
        source_bucket=BUCKET_NAME,
        source_object=CSV_SOURCE,
        destination_bucket=BUCKET_NAME,
        destination_object='data/archive/{{ task_instance.xcom_pull(task_ids="load_to_bigquery", key="return_value") }}',
        move_object=True,
        trigger_rule="all_success",  # This makes the task execute only if the previous tasks were successful
    )

    # Move file to error on failure
    move_file_to_error = GCSToGCSOperator(
        task_id="move_file_to_error",
        source_bucket=BUCKET_NAME,
        source_object=CSV_SOURCE,
        destination_bucket=BUCKET_NAME,
        destination_object='data/error/{{ task_instance.xcom_pull(task_ids="load_to_bigquery", key="return_value") }}',
        move_object=True,
        trigger_rule="one_failed",  # This makes the task execute if any of the previous tasks failed
    )

    # Define task dependencies
    create_dataset_task >> create_bq_table_task >> load_to_bq_task
    load_to_bq_task >> move_file_to_archive
    load_to_bq_task >> move_file_to_error
