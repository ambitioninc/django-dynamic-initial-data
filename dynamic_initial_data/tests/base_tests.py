from django.test import TestCase
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataManager
from dynamic_initial_data.tests.mocks import MockInitialData, MockClass


class BaseInitialDataTest(TestCase):
    """
    Tests the base classes
    """
    def test_base_initial_data(self):
        initial_data_base = BaseInitialData()
        # with self.assertRaises(NotImplemented):
        #     initial_data_base.update_static()

class InitialDataManagerTest(TestCase):
    """
    Tests the functionality of the InitialDataManager
    """
    def test_load_app(self):
        """
        Tests the load_app method
        """
        with patch('dynamic_initial_data.base.import_string') as import_patch:
            import_patch.return_value = MockInitialData
            initial_data_manager = InitialDataManager()
            self.assertEqual(MockInitialData, initial_data_manager.load_app('fake'))
            import_patch.return_value = MockClass
            self.assertIsNone(initial_data_manager.load_app('fake'))

    def test_update_app(self):
        """
        Tests the update_app method
        """
        pass

    def update_all_apps(self):
        """
        Verifies that update_app is called with all installed apps
        """
        pass

    def detect_dependency_cycles(self):
        """
        Makes sure that dependency cycles are found and raises an exception
        """
        pass
