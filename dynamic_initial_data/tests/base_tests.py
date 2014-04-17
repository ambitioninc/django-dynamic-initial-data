from django.test import TestCase
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataManager
from dynamic_initial_data.exceptions import InitialDataMissingApp
from dynamic_initial_data.tests.mocks import MockInitialData, MockClass, MockOne, MockTwo


class BaseInitialDataTest(TestCase):
    """
    Tests the base classes
    """
    def test_base_initial_data(self):
        initial_data = BaseInitialData()
        with self.assertRaises(NotImplementedError):
            initial_data.update_static()


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
        # make sure an error is raised for missing app
        initial_data_manager = InitialDataManager()
        with self.assertRaises(InitialDataMissingApp):
            initial_data_manager.update_app('fake')

        # make sure app gets added to updated apps
        initial_data_manager = InitialDataManager()
        with patch('dynamic_initial_data.base.InitialDataManager.get_class_path') as get_path_patch:
            get_path_patch.return_value = 'dynamic_initial_data.tests.mocks.MockInitialData'

            # patch the update_static method so we make sure it is called
            update_static_patcher = patch('dynamic_initial_data.tests.mocks.MockInitialData.update_static')
            update_static_patch = update_static_patcher.start()
            initial_data_manager.update_app('dynamic_initial_data')
            self.assertEqual(1, update_static_patch.call_count)

            # make sure it doesn't call update static again
            initial_data_manager.update_app('dynamic_initial_data')
            self.assertEqual(1, update_static_patch.call_count)

            # stop the patcher
            update_static_patcher.stop()

            # make sure the app is in the updated_apps list
            self.assertIn('dynamic_initial_data', initial_data_manager.updated_apps)

        # test dependencies
        def app_loader(app):
            if app == 'MockOne':
                return MockOne
            elif app == 'MockTwo':
                return MockTwo
            return None

        initial_data_manager = InitialDataManager()
        with patch('dynamic_initial_data.base.InitialDataManager.load_app') as load_app_patch:
            # get_path_patch.return_value = None
            load_app_patch.side_effect = app_loader

            # patch update_static methods
            update_static_patcher1 = patch('dynamic_initial_data.tests.mocks.MockOne.update_static')
            update_static_patcher2 = patch('dynamic_initial_data.tests.mocks.MockTwo.update_static')
            update_static_patch1 = update_static_patcher1.start()
            update_static_patch2 = update_static_patcher2.start()

            initial_data_manager.update_app('MockTwo')
            self.assertEqual(1, update_static_patch1.call_count)
            self.assertEqual(1, update_static_patch2.call_count)

            update_static_patcher1.stop()
            update_static_patcher2.stop()


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
