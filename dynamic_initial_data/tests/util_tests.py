from django.test import TestCase
from dynamic_initial_data.utils.import_string import import_string


class UtilTest(TestCase):
    """
    Tests the functions in the utils file
    """
    def test_import_string(self):
        """
        Tests all outcomes out import_string
        """
        # Make sure an invalid module path returns None
        self.assertIsNone(import_string('nope.nope'))

        # Make sure an invalid module name returns None
        self.assertIsNone(import_string('dynamic_initial_data.nope'))

        # For test coverage, import a null value
        self.assertIsNone(import_string('dynamic_initial_data.tests.mocks.mock_null_value'))

        # For test coverage, import a real class
        self.assertIsNotNone(import_string('dynamic_initial_data.tests.mocks.MockClass'))
