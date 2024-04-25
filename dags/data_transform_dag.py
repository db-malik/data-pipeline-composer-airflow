from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from google.cloud import bigquery

# Constants
SOURCE_DATASET_NAME = "raw"
SOURCE_TABLE_NAME = "RAW_SALES_TABLE"
TARGET_DATASET_NAME = "DATAWERHOUSE_TERRAFRM"
TARGET_TABLE_NAME = "transformed_Table"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["malek.dbouba@pm.me"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(1),
}


def truncate_target_table():
    client = bigquery.Client()
    sql_query = (
        f"TRUNCATE TABLE `{client.project}.{SOURCE_DATASET_NAME}.{SOURCE_TABLE_NAME}`"
    )
    query_job = client.query(sql_query)
    query_job.result()  # Wait for the query to complete


def load_transformed_data():
    client = bigquery.Client()
    transformation_sql = f"""
    INSERT INTO `{client.project}.{TARGET_DATASET_NAME}.{TARGET_TABLE_NAME}` (SaleID, ProductID, Quantity, Price, SaleDate)
    SELECT CAST (SaleID as INTEGER), CAST(ProductID as STRING) , CAST(quantity AS INTEGER), CAST( Price as FLOAT),  CAST(date AS DATE), quantity * price AS total_price
    FROM `{client.project}.{SOURCE_DATASET_NAME}.{SOURCE_TABLE_NAME}`;
    """
    query_job = client.query(transformation_sql)
    query_job.result()  # Wait for the query to complete


with DAG(
    dag_id="data_transformation_and_loading",
    default_args=default_args,
    description="A DAG for data transformation and loading into DWH",
    schedule_interval=timedelta(days=1),
) as dag:

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

    start >> truncate_table >> transform_load >> end
