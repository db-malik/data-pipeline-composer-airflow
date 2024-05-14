import unittest
from airflow.models import DagBag


class TestDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag(dag_folder="dags/", include_examples=False)

    def test_dag_loaded(self):
        """Check that the DAG file is syntactically correct and can be successfully imported."""
        dags = self.dagbag.dags
        self.assertIn(
            "dbouba_data_extraction_and_loading_dag",
            dags,
            "DAG 'dbouba_data_extraction_and_loading_dag' is not present in the DAG bag",
        )
        self.assertEqual(len(self.dagbag.import_errors), 0, "DAGs failed to import")

    def test_task_count(self):
        """Check if the correct number of tasks have been added to the DAG."""
        dag_id = "dbouba_data_extraction_and_loading_dag"
        dag = self.dagbag.get_dag(dag_id)
        self.assertEqual(len(dag.tasks), 6, "Number of tasks is not as expected")

    def test_dependencies_of_tasks(self):
        """Check the dependencies of tasks in the DAG."""
        dag_id = "your_dag_id"
        dag = self.dagbag.get_dag(dag_id)
        dependencies = {
            "start_task": {"second_task"},
            "second_task": {"end_task"},
            "end_task": set(),
        }

        for task_id, downstream_list in dependencies.items():
            task = dag.get_task(task_id)
            self.assertEqual(
                set(task.downstream_task_ids),
                downstream_list,
                f"Dependencies for {task_id} are incorrect",
            )


if __name__ == "__main__":
    unittest.main()
