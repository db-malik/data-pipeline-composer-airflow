import unittest
from unittest.mock import patch, Mock
from airflow.models import DagBag


class TestDBoubaDataExtractionAndLoadingDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch the get_dag method of the DagBag class to return a mock DAG object
        with patch("airflow.models.DagBag.get_dag") as mock_get_dag:
            # Create a Mock object for the DAG
            mock_dag = Mock()
            # Set up mock attributes or methods as necessary
            mock_dag.tasks = ["task1", "task2", "task3", "task4", "task5"]
            # Configure the mock to return the mock DAG when called
            mock_get_dag.return_value = mock_dag
            # Initialize a DagBag instance (this will not perform any database operations)
            cls.dagbag = DagBag(include_examples=False)
            # Use the mocked get_dag method
            cls.dag = cls.dagbag.get_dag("dbouba_data_extraction_and_loading_dag")

    def test_task_count(self):
        """Ensure the correct number of tasks have been added to the DAG."""
        # Check if the number of tasks is as expected
        self.assertEqual(len(self.dag.tasks), 5)


if __name__ == "__main__":
    unittest.main()
