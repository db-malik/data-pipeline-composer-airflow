from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from datetime import datetime
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator
import os


# Accessing the variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
RAW_DATASET = os.getenv("RAW_DATASET")

CSV_FILE_NAME = "SALES.csv"


# Define default arguments for the DAG: no retries, and start running on January 1st, 2024
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,  # No retries
    "start_date": datetime(2024, 1, 1),
    "catchup": False,
}

# DAG definition: runs daily at 10 AM UTC
with DAG(
    "data_extraction_and_loading_dag",
    default_args=default_args,
    description="Extract data from CSV and load into BigQuery",
    schedule_interval="0 10 * * *",  # Trigger daily at 10 AM UTC
    catchup=False,
) as dag:

    # Define tasks
    start = DummyOperator(
        task_id="start",
        dag=dag,
    )

    # Task to load CSV files from GCS to BigQuery
    load_to_bq_task = GCSToBigQueryOperator(
        task_id="load_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=[f"{DATA_FOLDER}/*.csv"],
        destination_project_dataset_table=f"{RAW_DATASET}.{RAW_SALES_TABLE}",
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
        field_delimiter=",",  # CSV delimiter is comma
        encoding="UTF-8",
    )

    # Move file to archive on success
    move_file_to_archive = GCSToGCSOperator(
        task_id="move_file_to_archive",
        source_bucket=BUCKET_NAME,
        source_object=f"{DATA_FOLDER}/{IN_FOLDER}/{CSV_FILE_NAME}",
        destination_bucket=BUCKET_NAME,
        destination_object=f"{DATA_FOLDER}/{ARCHIVE_FOLDER}/",
        move_object=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,  # This makes the task execute only if the previous tasks were successful
    )

    # Move file to error on failure
    move_file_to_error = GCSToGCSOperator(
        task_id="move_file_to_error",
        source_bucket=BUCKET_NAME,
        source_object=f"{DATA_FOLDER}/{IN_FOLDER}/{CSV_FILE_NAME}",
        destination_bucket=BUCKET_NAME,
        destination_object=f"{DATA_FOLDER}/{IN_FOLDER}/",
        move_object=True,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Trigger the second DAG after loading data to BigQuery
    trigger_second_dag = TriggerDagRunOperator(
        task_id="trigger_second_dag",
        trigger_dag_id="data_transformation_and_loading",
        conf={"message": "Triggered from first_dag"},
    )

    end = DummyOperator(
        task_id="end",
        dag=dag,
    )

    # Define task dependencies
    start >> load_to_bq_task >> trigger_second_dag
    load_to_bq_task >> move_file_to_archive >> end
    load_to_bq_task >> move_file_to_error >> end
