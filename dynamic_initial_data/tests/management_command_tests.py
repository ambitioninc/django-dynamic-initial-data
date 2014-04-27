from django.core.management import call_command
from django.test import TestCase
from mock import patch


class UpdateInitialDataTest(TestCase):
    """
    Tests each of the management commands
    """
    def test_no_arguments(self):
        """
        Makes sure the update_initial_data method gets called when the command is run
        """
        with patch('dynamic_initial_data.base.InitialDataUpdater.update_all_apps') as update_patch:
            call_command('update_initial_data')
            self.assertEqual(1, update_patch.call_count)

    def test_app_argument(self):
        """
        Tests the management command with the --app argument. Verifies that it runs for only the
        provided app.
        """
        with patch('dynamic_initial_data.base.InitialDataUpdater.update_app') as update_patch:
            call_command('update_initial_data', app='app_path')
            self.assertEqual(1, update_patch.call_count)
            update_patch.assert_called_with('app_path')
