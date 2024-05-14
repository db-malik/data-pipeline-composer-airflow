from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from datetime import datetime
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator  # instead of DummyOperator

import os


# Accessing the variables
# use environment variables to access the bucket name for security reasons
BUCKET_NAME = os.getenv("BUCKET_NAME")

RAW_DATASET = "rawdata"
IN_FOLDER = "in"
DATA_FOLDER = "DBOUBA/DATA"
RAW_SALES_TABLE = "RAW_DB_DATA"
ARCHIVE_FOLDER = "archive"
ERROR_FOLDER = "error"


# Define the schema fields
raw_table_schema = [
    {"name": "SaleID", "type": "STRING", "mode": "NULLABLE"},
    {"name": "ProductID", "type": "STRING", "mode": "NULLABLE"},
    {"name": "Quantity", "type": "STRING", "mode": "NULLABLE"},
    {"name": "Price", "type": "STRING", "mode": "NULLABLE"},
    {"name": "SaleDate", "type": "STRING", "mode": "NULLABLE"},
]


# Define default arguments for the DAG: no retries, and start running on January 1st, 2024
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,  # No retries
    # "start_date": datetime(2024, 1, 1),
    "start_date": datetime.now(),  # Set start date to current time just to reduce charge
    "catchup": False,
}

# DAG definition: runs daily at 10 AM UTC
with DAG(
    "dbouba_data_extraction_and_loading_dag",
    default_args=default_args,
    description="Extract data from CSV and load into BigQuery",
    schedule="0 10 * * *",  # Trigger daily at 10 AM UTC
    # schedule_interval=None,  # Do not schedule, run only manually comment ths ligne  and uncomment the under line for Trigger daily at 10:00
    catchup=False,
) as dag:

    # Define tasks
    start = EmptyOperator(
        task_id="start",
        dag=dag,
    )

    # Task to load CSV files from GCS to BigQuery
    load_to_bq_task = GCSToBigQueryOperator(
        task_id="load_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=[f"{DATA_FOLDER}/{IN_FOLDER}/*.csv"],
        destination_project_dataset_table=f"{RAW_DATASET}.{RAW_SALES_TABLE}",
        source_format="CSV",
        write_disposition="WRITE_TRUNCATE",
        schema_fields=raw_table_schema,
        skip_leading_rows=1,  # Skip the first row (header)
        autodetect=False,  # Explicit schema provided, so autodetect is not needed
        field_delimiter=",",  # CSV delimiter is comma
        encoding="UTF-8",
    )

    # Move file to archive on success
    move_file_to_archive = GCSToGCSOperator(
        task_id="move_file_to_archive",
        source_bucket=BUCKET_NAME,
        source_object=f"{DATA_FOLDER}/{IN_FOLDER}/*.csv",  # Use wildcard to match all CSV files
        destination_bucket=BUCKET_NAME,
        destination_object=f"{DATA_FOLDER}/{ARCHIVE_FOLDER}/",
        move_object=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,  # This makes the task execute only if the previous tasks were successful
    )

    # Move file to error on failure
    move_file_to_error = GCSToGCSOperator(
        task_id="move_file_to_error",
        source_bucket=BUCKET_NAME,
        source_object=f"{DATA_FOLDER}/{IN_FOLDER}/*.csv",  # Use wildcard to match all CSV files
        destination_bucket=BUCKET_NAME,
        destination_object=f"{DATA_FOLDER}/{ERROR_FOLDER}/",
        move_object=True,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Trigger the second DAG after loading data to BigQuery
    trigger_second_dag = TriggerDagRunOperator(
        task_id="trigger_second_dag",
        trigger_dag_id="dbouba_data_transformation_and_loading",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,  # Ensures this runs as long as one of the branches has succeeded without failures
        conf={"message": "Triggered from first_dag"},
    )

    end = EmptyOperator(
        task_id="end",
        dag=dag,
    )

    # Define task dependencies
    start >> load_to_bq_task

    # Branching to move file to archive or error based on a condition
    load_to_bq_task >> [move_file_to_archive, move_file_to_error]

    # Both branches eventually lead to triggering a second DAG
    [move_file_to_archive, move_file_to_error] >> trigger_second_dag

    # Finalize the DAG
    trigger_second_dag >> end
