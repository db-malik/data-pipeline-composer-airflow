import unittest
from airflow.models import DagBag


class TestAirflowDAGs(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_no_import_errors(self):
        self.assertFalse(
            self.dagbag.import_errors, "DAGs should not have import errors"
        )


if __name__ == "__main__":
    unittest.main()
