import pytest
from airflow.models import DagBag

# Initialize the DagBag object which will load DAGs from the specified folder
dag_bag = DagBag(dag_folder="./dags/", include_examples=False)


@pytest.fixture(scope="session")
def bag():
    # Provide a session-scoped fixture that returns the initialized DagBag
    # This fixture is reused across all tests in this session, improving test performance
    return dag_bag


def test_no_import_errors(bag):
    # Test to ensure there are no import errors in any of the DAGs
    # Import errors can occur if there are Python errors in the DAG files
    assert len(bag.import_errors) == 0, "DAGs should not have import errors"


def test_expected_number_of_tasks(bag):
    # Verify that each DAG contains the expected number of tasks
    # This helps ensure that no tasks are missing or unexpectedly added

    extraction_dag = bag.get_dag("dbouba_data_extraction_and_loading_dag")
    assert len(extraction_dag.tasks) == 7, "Extraction DAG should have 7 tasks"

    transformation_dag = bag.get_dag("dbouba_data_transformation_and_loading")
    assert len(transformation_dag.tasks) == 4, "Transformation DAG should have 4 tasks"


def test_dependencies_of_extraction_dag(bag):
    # Test to verify that the task dependencies in the extraction DAG are set up correctly
    # Correct dependencies are crucial for the DAG to execute in the intended order
    extraction_dag = bag.get_dag("dbouba_data_extraction_and_loading_dag")
    structure = {
        "start": {"load_to_bigquery"},
        "load_to_bigquery": {"move_file_to_archive", "move_file_to_error"},
        "move_file_to_archive": {"trigger_second_dag"},
        "move_file_to_error": {"trigger_second_dag"},
        "trigger_second_dag": {"end"},
        "end": set(),
    }
    for task_id, downstream_task_ids in structure.items():
        actual_downstream = set(
            task.downstream_task_ids
            for task in extraction_dag.get_task(task_id).downstream_list
        )
        assert (
            actual_downstream == downstream_task_ids
        ), f"Task {task_id} has incorrect downstream dependencies"


def test_dependencies_of_transformation_dag(bag):
    # Check that the task dependencies in the transformation DAG are as expected
    transformation_dag = bag.get_dag("dbouba_data_transformation_and_loading")
    structure = {
        "start": {"truncate_target_table"},
        "truncate_target_table": {"load_transformed_data"},
        "load_transformed_data": {"end"},
        "end": set(),
    }
    for task_id, downstream_task_ids in structure.items():
        actual_downstream = set(
            task.downstream_task_ids
            for task in transformation_dag.get_task(task_id).downstream_list
        )
        assert (
            actual_downstream == downstream_task_ids
        ), f"Task {task_id} has incorrect downstream dependencies"


def test_task_parameters(bag):
    # Test the configuration parameters of specific tasks to ensure they are set correctly
    dag = bag.get_dag("dbouba_data_extraction_and_loading_dag")
    task = dag.get_task("load_to_bigquery")
    assert (
        task.bucket == "gcs-viseo-data-academy-22024"
    ), "Incorrect bucket set for load_to_bigquery"
    assert task.source_format == "CSV", "Source format should be CSV"
    assert (
        task.write_disposition == "WRITE_TRUNCATE"
    ), "Write disposition should be WRITE_TRUNCATE"

    # Additional check for SQL logic in the transformation task of the second DAG
    # Typically, you might mock BigQuery client and assert SQL commands
    dag = bag.get_dag("dbouba_data_transformation_and_loading")
    transform_task = dag.get_task("load_transformed_data")
    assert (
        transform_task.python_callable.__name__ == "load_transformed_data"
    ), "Incorrect callable assigned to the task"
