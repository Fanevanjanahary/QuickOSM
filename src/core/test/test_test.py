
import unittest

from qgis.testing import start_app

# start_app()


class TestTest(unittest.TestCase):
    def test_check_parameters(self):
        """Test check parameters query."""
        self.assertEqual(2, 2)
