from django.core.management import call_command
from django.test import TestCase
from mock import patch


class SyncInitialDataTest(TestCase):

    def test_no_arguments(self):
        with patch('dynamic_initial_data.base.InitialDataManager.update_all_apps') as update_patch:
            call_command('sync_initial_data')
            self.assertEqual(1, update_patch.call_count)
