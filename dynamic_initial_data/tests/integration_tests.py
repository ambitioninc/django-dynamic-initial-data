from django.test import TestCase
from mock import patch

from dynamic_initial_data.base import BaseInitialData, InitialDataUpdater
from dynamic_initial_data.models import RegisteredForDeletionReceipt
from dynamic_initial_data.tests.models import Account


class IntegrationTest(TestCase):
    """
    Tests the full initial data process.
    """
    def test_create_account(self):
        """
        Tests creating a test account in the initial data process.
        """
        class AccountInitialData(BaseInitialData):
            def update_initial_data(self):
                Account.objects.get_or_create()

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData) as load_app_mock:
            InitialDataUpdater().update_app('test_app')
            # It should be called twice - once for initial loading, and twice for dependency testing
            self.assertEquals(load_app_mock.call_count, 2)

        # Verify an account object was created
        self.assertEquals(Account.objects.count(), 1)

    def test_multiple_same_objects(self):
        """
        Tests initial data when registering the same object for deletion twice.
        """
        class AccountInitialData1(BaseInitialData):
            """
            Initial data code that registers the same object many times for deletion
            """
            def update_initial_data(self):
                # Return the object from update_initial_data, thus registering it for deletion
                account = Account.objects.get_or_create()[0]
                return [account, account, account]

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData1):
            InitialDataUpdater().update_all_apps()
            InitialDataUpdater().update_all_apps()

        # Verify an account object was created and is managed by a deletion receipt
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)

    def test_handle_deletions_returned_from_update_initial_data(self):
        """
        Tests handling of deletions when they are returned from the update_initial_data function.
        """
        class AccountInitialData1(BaseInitialData):
            """
            The initial data code the first time it is called. It registers an account for deletion
            by returning it from the update_initial_data function.
            """
            def update_initial_data(self):
                # Return the object from update_initial_data, thus registering it for deletion
                return [Account.objects.get_or_create()[0]]

        class AccountInitialData2(BaseInitialData):
            """
            The initial data code the second time it is called. It no longer creates the account object, so the
            previously created account object should be deleted.
            """
            def update_initial_data(self):
                pass

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData1):
            InitialDataUpdater().update_all_apps()

        # Verify an account object was created and is managed by a deletion receipt
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)

        # Run the initial data process again, this time not registering the account for
        # deletion. It should be deleted.
        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData2):
            InitialDataUpdater().update_all_apps()

        # Verify there are no accounts or receipts
        self.assertEquals(Account.objects.count(), 0)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)

    def test_handle_deletions_updates_returned_from_update_initial_data(self):
        """
        Tests handling of deletions and updates when they are returned from the update_initial_data function.
        """
        class AccountInitialData1(BaseInitialData):
            """
            The initial data code the first time it is called. It registers two accounts for deletion
            by returning it from the update_initial_data function.
            """
            def update_initial_data(self):
                # Return the object from update_initial_data, thus registering it for deletion
                return [Account.objects.get_or_create(name='hi')[0], Account.objects.get_or_create(name='hi2')[0]]

        class AccountInitialData2(BaseInitialData):
            """
            The initial data code the second time it is called. It only manages one of the previous accounts
            """
            def update_initial_data(self):
                return [Account.objects.get_or_create(name='hi')[0]]

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData1):
            InitialDataUpdater().update_all_apps()

        # Verify two account objects were created and are managed by deletion receipts
        self.assertEquals(Account.objects.count(), 2)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 2)

        # Run the initial data process again, this time deleting the account named 'hi2'
        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData2):
            InitialDataUpdater().update_all_apps()

        # Verify only the 'hi' account exists
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.get().model_obj.name, 'hi')

    def test_handle_deletions_registered_from_update_initial_data(self):
        """
        Tests handling of deletions when they are programmatically registered from the update_initial_data function.
        """
        class AccountInitialData1(BaseInitialData):
            """
            The initial data code the first time it is called. It registers an account for deletion
            by returning it from the update_initial_data function.
            """
            def update_initial_data(self):
                # Register the object for deletion
                self.register_for_deletion(Account.objects.get_or_create()[0])

        class AccountInitialData2(BaseInitialData):
            """
            The initial data code the second time it is called. It no longer creates the account object, so the
            previously created account object should be deleted.
            """
            def update_initial_data(self):
                pass

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData1):
            InitialDataUpdater().update_all_apps()

        # Verify an account object was created and is managed by a deletion receipt
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)

        # Run the initial data process again, this time not registering the account for
        # deletion. It should be deleted.
        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData2):
            InitialDataUpdater().update_all_apps()

        # Verify there are no accounts or receipts
        self.assertEquals(Account.objects.count(), 0)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 0)

    def test_handle_deletions_updates_registered_from_update_initial_data(self):
        """
        Tests handling of deletions and updates when they are registered from the update_initial_data function.
        """
        class AccountInitialData1(BaseInitialData):
            """
            The initial data code the first time it is called. It registers two accounts for deletion
            by returning it from the update_initial_data function.
            """
            def update_initial_data(self):
                # Register two account objects for deletion
                self.register_for_deletion(
                    Account.objects.get_or_create(name='hi')[0], Account.objects.get_or_create(name='hi2')[0])

        class AccountInitialData2(BaseInitialData):
            """
            The initial data code the second time it is called. It only manages one of the previous accounts
            """
            def update_initial_data(self):
                self.register_for_deletion(Account.objects.get_or_create(name='hi')[0])

        # Verify no account objects exist
        self.assertEquals(Account.objects.count(), 0)

        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData1):
            InitialDataUpdater().update_all_apps()

        # Verify two account objects were created and are managed by deletion receipts
        self.assertEquals(Account.objects.count(), 2)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 2)

        # Run the initial data process again, this time deleting the account named 'hi2'
        with patch.object(InitialDataUpdater, 'load_app', return_value=AccountInitialData2):
            InitialDataUpdater().update_all_apps()

        # Verify only the 'hi' account exists
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.count(), 1)
        self.assertEquals(RegisteredForDeletionReceipt.objects.get().model_obj.name, 'hi')
