from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import bigquery
from airflow.exceptions import AirflowException

import os


# Accessing the variables
RAW_DATASET = os.getenv("RAW_DATASET")
RAW_SALES_TABLE = os.getenv("RAW_SALES_TABLE")
DATAWERHOUSE_DATASET = os.getenv("DATAWERHOUSE_DATASET")
DWH_TABLE = os.getenv("DWH_TABLE")


# Function to truncate the target table before loading new data
def truncate_target_table():
    client = bigquery.Client()

    # Compose the SQL statement for truncating the table
    sql_query = f"TRUNCATE TABLE `{client.project}.{DATAWERHOUSE_DATASET}.{DWH_TABLE}`"

    try:
        query_job = client.query(sql_query)
        query_job.result()
        print("Table truncated successfully.")
    except bigquery.exceptions.GoogleCloudError as e:
        # Handle exceptions related to Google Cloud operations
        print(f"Failed to truncate table due to a Google Cloud error: {e}")
        raise AirflowException(f"BigQuery task failed: {e}")
    except Exception as e:
        # Handle other unforeseen exceptions
        print(f"An unexpected error occurred: {e}")
        raise AirflowException(f"Unexpected error in BigQuery task: {e}")


# Function to transform and load data into the target table
def load_transformed_data():
    client = bigquery.Client()

    transformation_sql_query = f"""
    INSERT INTO `{client.project}.{DATAWERHOUSE_DATASET}.{DWH_TABLE}` (SaleID, ProductID, Quantity, Price, SaleDate, TotalPrice)
    SELECT CAST(SaleID as INTEGER), CAST(ProductID as STRING), CAST(quantity AS INTEGER),  CAST(Price AS NUMERIC), CAST(SaleDate AS DATE), CAST(CAST(quantity AS NUMERIC) * CAST(Price AS NUMERIC) AS NUMERIC) AS TotalPrice
    FROM `{client.project}.{RAW_DATASET}.{RAW_SALES_TABLE}`;
    """

    try:
        query_job = client.query(transformation_sql_query)
        result = query_job.result()  # Wait for the query to complete
        print("Query results:", list(result))
    except Exception as e:
        print("Failed to execute query:", str(e))
        raise


# DAG definition ----------------------------------

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 0,  # No retries
    "start_date": days_ago(1),
}


with DAG(
    dag_id="data_transformation_and_loading",
    default_args=default_args,
    description="A DAG for data transformation and loading into DWH",
    schedule_interval=timedelta(days=1),
) as dag:

    # Define tasks
    start = DummyOperator(
        task_id="start",
        dag=dag,
    )

    truncate_table = PythonOperator(
        task_id="truncate_target_table",
        python_callable=truncate_target_table,
        dag=dag,
    )

    transform_load = PythonOperator(
        task_id="load_transformed_data",
        python_callable=load_transformed_data,
        dag=dag,
    )

    end = DummyOperator(
        task_id="end",
        dag=dag,
    )

    # Define task dependencies--------------------------
    start >> truncate_table >> transform_load >> end
