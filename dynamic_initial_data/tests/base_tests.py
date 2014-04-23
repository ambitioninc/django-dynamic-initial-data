from django.conf import settings
from django.test import TestCase
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataUpdater
from dynamic_initial_data.exceptions import InitialDataMissingApp, InitialDataCircularDependency
from dynamic_initial_data.tests.mocks import MockInitialData, MockClass, MockOne, MockTwo, MockThree


class BaseInitialDataTest(TestCase):
    """
    Tests the base classes
    """
    def test_base_initial_data(self):
        initial_data = BaseInitialData()
        with self.assertRaises(NotImplementedError):
            initial_data.update_initial_data()


class InitialDataUpdaterTest(TestCase):
    """
    Tests the functionality of the InitialDataUpdater
    """
    def test_verbose_option(self):
        """
        Verifies that the verbose option gets set from the manage options
        """
        options = {'verbose': True}
        initial_data_manager = InitialDataUpdater(options)
        self.assertTrue(initial_data_manager.verbose)
        # cover the branch that prints if verbose is true
        initial_data_manager.log('test')

    def test_load_app(self):
        """
        Tests the load_app method
        """
        with patch('dynamic_initial_data.base.import_string') as import_patch:
            import_patch.return_value = MockInitialData
            initial_data_manager = InitialDataUpdater()
            self.assertEqual(MockInitialData, initial_data_manager.load_app('fake'))

            # try to load an app that doesn't exist
            initial_data_manager = InitialDataUpdater()
            import_patch.return_value = MockClass
            self.assertIsNone(initial_data_manager.load_app('fake'))

    def test_update_app(self):
        """
        Tests the update_app method
        """
        # an error should only be raised for missing dependencies and not for directly
        # calling update on an app that doesn't have an initial data file
        initial_data_manager = InitialDataUpdater()
        initial_data_manager.update_app('fake')

        # make sure app gets added to updated apps
        initial_data_manager = InitialDataUpdater()
        with patch('dynamic_initial_data.base.InitialDataUpdater.get_class_path', spec_set=True) as get_path_patch:
            get_path_patch.return_value = 'dynamic_initial_data.tests.mocks.MockInitialData'

            # patch the update_initial_data method so we make sure it is called
            update_initial_data_patcher = patch('dynamic_initial_data.tests.mocks.MockInitialData.update_initial_data')
            update_initial_data_patch = update_initial_data_patcher.start()
            initial_data_manager.update_app('dynamic_initial_data')
            self.assertEqual(1, update_initial_data_patch.call_count)

            # make sure it doesn't call update static again
            initial_data_manager.update_app('dynamic_initial_data')
            self.assertEqual(1, update_initial_data_patch.call_count)

            # stop the patcher
            update_initial_data_patcher.stop()

            # make sure the app is in the updated_apps list
            self.assertIn('dynamic_initial_data', initial_data_manager.updated_apps)

        # test dependencies
        def app_loader(app):
            if app == 'MockOne':
                return MockOne
            elif app == 'MockTwo':
                return MockTwo
            return None

        # coverage
        app_loader(None)

        initial_data_manager = InitialDataUpdater()
        with patch('dynamic_initial_data.base.InitialDataUpdater.load_app', spec_set=True) as load_app_patch:
            load_app_patch.side_effect = app_loader

            # patch update_initial_data methods
            update_initial_data_patcher1 = patch('dynamic_initial_data.tests.mocks.MockOne.update_initial_data')
            update_initial_data_patcher2 = patch('dynamic_initial_data.tests.mocks.MockTwo.update_initial_data')
            update_initial_data_patch1 = update_initial_data_patcher1.start()
            update_initial_data_patch2 = update_initial_data_patcher2.start()

            initial_data_manager.update_app('MockTwo')
            self.assertEqual(1, update_initial_data_patch1.call_count)
            self.assertEqual(1, update_initial_data_patch2.call_count)

            update_initial_data_patcher1.stop()
            update_initial_data_patcher2.stop()

    def test_update_all_apps(self):
        """
        Verifies that update_app is called with all installed apps
        """
        num_apps = len(settings.INSTALLED_APPS)
        with patch('dynamic_initial_data.base.InitialDataUpdater.update_app', spec_set=True) as update_app_patch:
            initial_data_manager = InitialDataUpdater()
            initial_data_manager.update_all_apps()
            self.assertEqual(num_apps, update_app_patch.call_count)

    def test_get_dependency_call_list(self):
        """
        Makes sure that dependency cycles are found and raises an exception
        """
        initial_data_manager = InitialDataUpdater()
        with patch('dynamic_initial_data.base.InitialDataUpdater.load_app', spec_set=True) as load_app_patch:
            load_app_patch.return_value = MockThree

            with self.assertRaises(InitialDataCircularDependency):
                initial_data_manager.update_app('MockThree')

        initial_data_manager = InitialDataUpdater()
        with self.assertRaises(InitialDataMissingApp):
            initial_data_manager.get_dependency_call_list('fake')
