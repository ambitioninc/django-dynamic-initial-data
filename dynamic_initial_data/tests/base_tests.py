from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G
from freezegun import freeze_time
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataUpdater
from dynamic_initial_data.exceptions import InitialDataMissingApp, InitialDataCircularDependency
from dynamic_initial_data.models import RegisteredForDeletionReceipt
from dynamic_initial_data.tests.mocks import MockInitialData, MockClass, MockOne, MockTwo, MockThree
from dynamic_initial_data.tests.models import Account


class BaseInitialDataTest(TestCase):
    """
    Tests the base classes
    """
    def test_base_initial_data(self):
        initial_data = BaseInitialData()
        with self.assertRaises(NotImplementedError):
            initial_data.update_initial_data()

    def test_register_for_deletion_one_arg(self):
        """
        Tests the register_for_deletion_function with one argument.
        """
        initial_data = BaseInitialData()
        account = G(Account)
        initial_data.register_for_deletion(account)
        self.assertEquals(initial_data.get_model_objs_registered_for_deletion(), [account])

    def test_register_for_deletion_multiple_args(self):
        """
        Tests the register_for_deletion_function with multiple arguments.
        """
        initial_data = BaseInitialData()
        account1 = G(Account)
        account2 = G(Account)
        initial_data.register_for_deletion(account1, account2)
        self.assertEquals(initial_data.get_model_objs_registered_for_deletion(), [account1, account2])


class TestHandleDeletions(TestCase):
    """
    Tests the handle_deletions functionality in the InitialDataUpater class.
    """
    def setUp(self):
        super(TestHandleDeletions, self).setUp()
        self.initial_data_updater = InitialDataUpdater()

    def test_handle_deletions_no_objs(self):
        """
        Tests when there are no objs to handle. The function should not raise any exceptions.
        """
        self.initial_data_updater.handle_deletions()

    def test_create_one_obj(self):
        """
        Tests creating one object to handle for deletion.
        """
        account = G(Account)
        self.initial_data_updater.model_objs_registered_for_deletion = [account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        receipt = RegisteredForDeletionReceipt.objects.get()
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

    def test_create_delete_one_obj(self):
        """
        Tests creating one object to handle for deletion and then deleting it.
        """
        account = G(Account)
        self.initial_data_updater.model_objs_registered_for_deletion = [account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        receipt = RegisteredForDeletionReceipt.objects.get()
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

        # Now, don't register the object for deletion and run it again at a different time
        self.initial_data_updater.model_objs_registered_for_deletion = []
        with freeze_time('2013-04-12 05:00:00'):
            self.initial_data_updater.handle_deletions()
        # The object should be deleted, along with its receipt
        self.assertEquals(Account.objects.count(), 0)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)

    def test_create_update_one_obj(self):
        """
        Tests creating one object to handle for deletion and then updating it.
        """
        account = G(Account)
        self.initial_data_updater.model_objs_registered_for_deletion = [account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        receipt = RegisteredForDeletionReceipt.objects.get()
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

        # Run the deletion handler again at a different time. It should not delete the object
        with freeze_time('2013-04-12 05:00:00'):
            self.initial_data_updater.handle_deletions()
        # The object should not be deleted, along with its receipt
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.get().register_time, datetime(2013, 4, 12, 5))

    def test_delete_already_deleted_obj(self):
        """
        Tests the case when an object that was registered for deletion has already been deleted.
        """
        account = G(Account)
        self.initial_data_updater.model_objs_registered_for_deletion = [account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        receipt = RegisteredForDeletionReceipt.objects.get()
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

        # Delete the model object. The receipt should still exist
        account.delete()
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)

        # Now, don't register the object for deletion and run it again at a different time
        self.initial_data_updater.model_objs_registered_for_deletion = []
        with freeze_time('2013-04-12 05:00:00'):
            self.initial_data_updater.handle_deletions()
        # The object should be deleted, along with its receipt
        self.assertEquals(Account.objects.count(), 0)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)


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
