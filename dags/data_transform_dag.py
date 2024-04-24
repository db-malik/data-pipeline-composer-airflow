from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

# Constants
SOURCE_DATASET_NAME = "raw_dataset"
TARGET_DATASET_NAME = "DATAWERHOUSE_TERRAFRM"
TABLE_NAME = "transformed_Table"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["your.email@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(1),
}


def truncate_target_table():
    sql = f"TRUNCATE TABLE {TARGET_DATASET_NAME}.{TABLE_NAME};"
    hook = BigQueryHook()
    hook.run(sql)


def load_transformed_data():
    transformation_sql = f"""
    INSERT INTO {TARGET_DATASET_NAME}.{TABLE_NAME} (id, date, quantity, price, total_price)
    SELECT id, CAST(date AS DATE), CAST(quantity AS NUMERIC), CAST(price AS NUMERIC), quantity * price AS total_price
    FROM {SOURCE_DATASET_NAME}.raw_table;
    """
    hook = BigQueryHook()
    hook.run(transformation_sql)


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
