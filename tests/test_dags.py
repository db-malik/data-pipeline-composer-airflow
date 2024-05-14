import unittest
from airflow.models import DagBag


class TestDBoubaDataExtractionAndLoadingDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the DAGs from your specified folder
        cls.dagbag = DagBag(dag_folder="./dags/", include_examples=False)

    def test_dag_loaded(self):
        """Ensure that the DAG file is syntactically correct."""
        dags = self.dagbag.dags
        self.assertIn("dbouba_data_extraction_and_loading_dag", dags, "DAG not found")

    def test_task_count(self):
        """Check if the correct number of tasks have been added to the DAG."""
        dag_id = "dbouba_data_extraction_and_loading_dag"
        dag = self.dagbag.get_dag(dag_id)
        self.assertEqual(len(dag.tasks), 6, "Number of tasks is not as expected")


if __name__ == "__main__":
    unittest.main()
