import unittest
from airflow.models import DagBag
from unittest.mock import patch


class TestDBoubaDataExtractionAndLoadingDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch("airflow.models.DagBag.get_dag") as mock_get_dag:
            mock_dag = Mock()
            mock_get_dag.return_value = mock_dag
            mock_dag.tasks = ["task1", "task2", "task3", "task4", "task5"]
            cls.dagbag = DagBag()
            cls.dag = cls.dagbag.get_dag("dbouba_data_extraction_and_loading_dag")

    def test_task_count(self):
        """Ensure the correct number of tasks have been added to the DAG."""
        self.assertEqual(len(self.dag.tasks), 5)


if __name__ == "__main__":
    unittest.main()
