import unittest
from unittest.mock import patch
from airflow.models import DagBag


class TestDBoubaDataExtractionAndLoadingDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag(dag_folder="dags/", include_examples=False)
        cls.dag = cls.dagbag.get_dag(dag_id="dbouba_data_extraction_and_loading_dag")

    def test_dag_loaded(self):
        """Ensure that the DAG is in the DagBag."""
        self.assertIn("dbouba_data_extraction_and_loading_dag", self.dagbag.dags)
        self.assertEqual(len(self.dagbag.import_errors), 0, "DAGs failed to import")

    @patch(
        "airflow.providers.google.cloud.transfers.gcs_to_bigquery.GCSToBigQueryOperator.execute"
    )
    @patch(
        "airflow.providers.google.cloud.transfers.gcs_to_gcs.GCSToGCSOperator.execute"
    )
    def test_task_dependencies(self, mock_gcs_to_bq, mock_gcs_to_gcs):
        """Check the task dependencies within the dag."""
        load_to_bq_task = self.dag.task_dict["load_to_bigquery"]
        archive_task = self.dag.task_dict["move_file_to_archive"]
        error_task = self.dag.task_dict["move_file_to_error"]
        trigger_task = self.dag.task_dict["trigger_second_dag"]

        self.assertTrue(
            list(load_to_bq_task.downstream_task_ids)
            == ["move_file_to_archive", "move_file_to_error"]
        )
        self.assertTrue(
            list(archive_task.downstream_task_ids) == ["trigger_second_dag"]
        )
        self.assertTrue(list(error_task.downstream_task_ids) == ["trigger_second_dag"])
        self.assertTrue(list(trigger_task.downstream_task_ids) == ["end"])


if __name__ == "__main__":
    unittest.main()
