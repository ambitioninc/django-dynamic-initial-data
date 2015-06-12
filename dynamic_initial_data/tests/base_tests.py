from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django_dynamic_fixture import G
from freezegun import freeze_time
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataUpdater
from dynamic_initial_data.exceptions import InitialDataMissingApp, InitialDataCircularDependency
from dynamic_initial_data.models import RegisteredForDeletionReceipt
from dynamic_initial_data.tests.mocks import MockInitialData, MockClass, MockOne, MockTwo, MockThree
from dynamic_initial_data.tests.models import Account, ProxyAccount, CantCascadeModel, RelModel


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


class TestInvalidDeletions(TransactionTestCase):
    def test_cant_delete_obj_in_receipt(self):
        """
        Tests when the object in the receipt cant be deleted such as a deleted content type
        or another model that cant be cascaded.
        """
        initial_data_updater = InitialDataUpdater()
        rel_model = G(RelModel)
        G(CantCascadeModel, rel_model=rel_model)
        RegisteredForDeletionReceipt.objects.create(model_obj=rel_model, register_time=datetime(2013, 4, 5))

        account = G(Account)
        RegisteredForDeletionReceipt.objects.create(model_obj=account, register_time=datetime(2013, 4, 5))
        initial_data_updater.model_objs_registered_for_deletion = []

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 2)
        with transaction.atomic():
            initial_data_updater.handle_deletions()
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)


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

    def test_create_dup_objs(self):
        """
        Tests creating duplicate objects for deletion.
        """
        account = G(Account)
        self.initial_data_updater.model_objs_registered_for_deletion = [account, account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        receipt = RegisteredForDeletionReceipt.objects.get()
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

    def test_create_dup_proxy_objs(self):
        """
        Tests creating duplicate objects for deletion when one is a proxy of another.
        """
        account = G(Account)
        proxy_account = ProxyAccount.objects.get(id=account.id)
        self.initial_data_updater.model_objs_registered_for_deletion = [account, account, proxy_account]

        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)
        with freeze_time('2013-04-12'):
            self.initial_data_updater.handle_deletions()
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 2)

        receipt = RegisteredForDeletionReceipt.objects.get(model_obj_type=ContentType.objects.get_for_model(account))
        self.assertEquals(receipt.model_obj_type, ContentType.objects.get_for_model(Account))
        self.assertEquals(receipt.model_obj_id, account.id)
        self.assertEquals(receipt.register_time, datetime(2013, 4, 12))

        receipt = RegisteredForDeletionReceipt.objects.get(
            model_obj_type=ContentType.objects.get_for_model(proxy_account, for_concrete_model=False))
        self.assertEquals(
            receipt.model_obj_type, ContentType.objects.get_for_model(ProxyAccount, for_concrete_model=False))
        self.assertEquals(receipt.model_obj_id, proxy_account.id)
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

    @patch('dynamic_initial_data.base.import_string', return_value=MockInitialData)
    def test_load_app_exists(self, import_patch):
        """
        Tests the load_app method on an app that exists
        """
        self.assertEqual(MockInitialData, InitialDataUpdater().load_app('fake'))

    @patch('dynamic_initial_data.base.import_string', return_value=MockInitialData)
    def test_load_app_cached(self, import_patch):
        """
        Tests that the cache is hit since import is only called once.
        """
        initial_data_updater = InitialDataUpdater()
        initial_data_updater.load_app('fake')
        initial_data_updater.load_app('fake')
        initial_data_updater.load_app('fake')
        self.assertEquals(import_patch.call_count, 1)

    @patch('dynamic_initial_data.base.import_string', return_value=MockClass)
    def test_load_app_doesnt_exist(self, import_patch):
        """
        Tests the load_app method on an app that doesnt exist
        """
        self.assertIsNone(InitialDataUpdater().load_app('fake'))

    @patch.object(InitialDataUpdater, 'load_app', return_value=MockInitialData, spec_set=True)
    def test_update_app_no_errors_raised(self, mock_load_app):
        """
        Tests the update_app method. No errors should be raised since it has all of the required
        components
        """
        InitialDataUpdater().update_app('fake')

    def test_update_app_cant_load_initial_data(self):
        """
        Tests when the initial data class can't be loaded. It should execute without error
        """
        InitialDataUpdater().update_app('bad_app_path')

    @patch.object(InitialDataUpdater, 'load_app', return_value=MockInitialData, spec_set=True)
    @patch('dynamic_initial_data.tests.mocks.MockInitialData.update_initial_data', spec_set=True)
    def test_update_app_cached_updated_apps(self, update_initial_data_patch, mock_load_app):
        """
        Tests that the app gets added to updated apps and it is cached
        """
        initial_data_manager = InitialDataUpdater()
        initial_data_manager.update_app('dynamic_initial_data')
        self.assertEqual(1, update_initial_data_patch.call_count)

        # make sure it doesn't call update static again
        initial_data_manager.update_app('dynamic_initial_data')
        self.assertEqual(1, update_initial_data_patch.call_count)

        # make sure the app is in the updated_apps list
        self.assertIn('dynamic_initial_data', initial_data_manager.updated_apps)

    @patch('dynamic_initial_data.tests.mocks.MockOne.update_initial_data', spec_set=True)
    @patch('dynamic_initial_data.tests.mocks.MockTwo.update_initial_data', spec_set=True)
    def test_update_app_dependencies(self, update_initial_data_patch2, update_initial_data_patch1):
        """
        Tests the update_app method when there are dependencies.
        """
        # test dependencies
        def app_loader(app):
            if app == 'MockOne':
                return MockOne
            else:
                return MockTwo

        with patch.object(InitialDataUpdater, 'load_app', side_effect=app_loader, spec_set=True):
            InitialDataUpdater().update_app('MockTwo')
            self.assertEqual(1, update_initial_data_patch1.call_count)
            self.assertEqual(1, update_initial_data_patch2.call_count)

    @override_settings(INSTALLED_APPS=('django.contrib.auth', 'django.contrib.admin',))
    @patch('dynamic_initial_data.base.InitialDataUpdater.update_app', spec_set=True)
    def test_update_all_apps(self, update_app_patch):
        """
        Verifies that update_app is called with all installed apps
        """
        initial_data_manager = InitialDataUpdater()
        initial_data_manager.update_all_apps()
        self.assertEqual(2, update_app_patch.call_count)

    @patch('dynamic_initial_data.base.InitialDataUpdater.load_app', return_value=MockThree, spec_set=True)
    def test_get_dependency_call_list_circular_dependency(self, load_app_patch):
        """
        Tests when a circular dependency is found
        """
        with self.assertRaises(InitialDataCircularDependency):
            InitialDataUpdater().update_app('MockThree')

    def test_get_dependency_call_list_initial_data_missing(self):
        """
        Tests when the initial data is missing.
        """
        with self.assertRaises(InitialDataMissingApp):
            InitialDataUpdater().get_dependency_call_list('fake')
