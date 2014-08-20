from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.transaction import atomic
from django.utils.module_loading import import_by_path

from dynamic_initial_data.exceptions import InitialDataCircularDependency, InitialDataMissingApp
from dynamic_initial_data.models import RegisteredForDeletionReceipt


class BaseInitialData(object):
    """
    Base class for handling initial data for an app. Subclasses are expected to implement the
    `update_initial_data` method to handle any data creation / modifications. The dependencies list
    should contain strings of the app names that are required to be initialized first. These
    app names should be the full app path equivalent to how it is defined in settings.INSTALLED_APPS
    Example:
        dependencies = ['my_app', 'my_other_app']
    """
    dependencies = []

    def __init__(self):
        # Keep track of any model objects that have been registered for deletion
        self.model_objs_registered_for_deletion = []

    def get_model_objs_registered_for_deletion(self):
        return self.model_objs_registered_for_deletion

    def register_for_deletion(self, *model_objs):
        """
        Registers model objects for deletion. This means the model object will be deleted from the system when it is
        no longer being managed by the initial data process.
        """
        self.model_objs_registered_for_deletion.extend(model_objs)

    def update_initial_data(self, *args, **kwargs):
        """
        Raises an error if the subclass does not implement this
        """
        raise NotImplementedError('{0} did not implement update_initial_data'.format(self))


class InitialDataUpdater(object):
    """
    This object is created to handle the updating process of an app or multiple apps. A cache is
    built of the updated apps, so the same app is never initialized more than once. Handles the loading
    and running of initialization classes.
    """
    def __init__(self, options=None):
        # Various options that can be passed to the initial data updater
        options = options or {}
        self.verbose = options.get('verbose', False)

        # Apps that have been updated so far. This allows us to process dependencies on other app
        # inits easier without performing redundant work
        self.updated_apps = set()

        # A cache of the apps that have been imported for data initialization
        self.loaded_apps = {}

        # A list of all models that have been registered for deletion
        self.model_objs_registered_for_deletion = []

    def get_class_path(self, app):
        """
        Builds the full path to the initial data class based on the specified app.
        :param app: The name of the app in which to get the initial data class. This should be the same
            path as defined in settings.INSTALLED_APPS
        :type app: str
        :return: The full import path to the initial data class
        :rtype: str
        """
        return '{0}.fixtures.initial_data.InitialData'.format(app)

    def load_app(self, app):
        """
        Tries to load an initial data class for a specified app. If the specified file does not exist,
        an error will be raised. If the class does exist, but it isn't a subclass of `BaseInitialData`
        then None will be returned.
        :param app: The name of the app in which to load the initial data class. This should be the same
            path as defined in settings.INSTALLED_APPS
        :type app: str
        :return: A subclass instance of BaseInitialData or None
        :rtype: BaseInitialData or None
        """
        if self.loaded_apps.get(app):
            return self.loaded_apps.get(app)

        self.loaded_apps[app] = None
        initial_data_class = import_by_path(self.get_class_path(app))
        if issubclass(initial_data_class, BaseInitialData):
            self.log('Loaded app {0}'.format(app))
            self.loaded_apps[app] = initial_data_class

        return self.loaded_apps[app]

    @atomic
    def update_app(self, app):
        """
        Loads and runs `update_initial_data` of the specified app. Any dependencies contained within the
        initial data class will be run recursively. Dependency cycles are checked for and a cache is built
        for updated apps to prevent updating the same app more than once.
        :param app: The name of the app to update. This should be the same path as defined
            in settings.INSTALLED_APPS
        :type app: str
        """
        # don't update this app if it has already been updated
        if app in self.updated_apps:
            return

        # load the initial data class
        try:
            initial_data_class = self.load_app(app)
        except ImproperlyConfigured:
            self.log('Could not load {0}'.format(app))
            return

        self.log('Checking dependencies for {0}'.format(app))

        # get dependency list
        dependencies = self.get_dependency_call_list(app)

        # update initial data of dependencies
        for dependency in dependencies:
            self.update_app(dependency)

        self.log('Updating app {0}'.format(app))

        # Update the initial data of the app and gather any objects returned for deletion. Objects registered for
        # deletion can either be returned from the update_initial_data function or programmatically added with the
        # register_for_deletion function in the BaseInitialData class.
        initial_data_instance = initial_data_class()
        model_objs_registered_for_deletion = initial_data_instance.update_initial_data() or []
        model_objs_registered_for_deletion.extend(initial_data_instance.get_model_objs_registered_for_deletion())

        # Add the objects to be deleted from the app to the global list of objects to be deleted.
        self.model_objs_registered_for_deletion.extend(model_objs_registered_for_deletion)

        # keep track that this app has been updated
        self.updated_apps.add(app)

    def handle_deletions(self):
        """
        Manages handling deletions of objects that were previously managed by the initial data process but no longer
        managed. It does so by mantaining a list of receipts for model objects that are registered for deletion on
        each round of initial data processing. Any receipts that are from previous rounds and not the current
        round will be deleted.
        """
        # Create receipts for every object registered for deletion
        now = datetime.utcnow()
        registered_for_deletion_receipts = [
            RegisteredForDeletionReceipt(
                model_obj_type=ContentType.objects.get_for_model(model_obj, for_concrete_model=False),
                model_obj_id=model_obj.id,
                register_time=now)
            for model_obj in set(self.model_objs_registered_for_deletion)
        ]

        # Do a bulk upsert on all of the receipts, updating their registration time.
        RegisteredForDeletionReceipt.objects.bulk_upsert(
            registered_for_deletion_receipts, ['model_obj_type_id', 'model_obj_id'], update_fields=['register_time'])

        # Delete all receipts and their associated model objects that weren't updated
        for receipt in RegisteredForDeletionReceipt.objects.exclude(register_time=now):
            try:
                receipt.model_obj.delete()
            except:
                # The model object may no longer be there, its ctype may be invalid, or it might be protected.
                # Regardless, the model object cannot be deleted, so go ahead and delete its receipt.
                pass
            receipt.delete()

    @atomic
    def update_all_apps(self):
        """
        Loops through all app names contained in settings.INSTALLED_APPS and calls `update_app`
        on each one. Handles any object deletions that happened after all apps have been initialized.
        """
        for app in settings.INSTALLED_APPS:
            self.update_app(app)

        # During update_app, all apps added model objects that were registered for deletion.
        # Delete all objects that were previously managed by the initial data process
        self.handle_deletions()

    def get_dependency_call_list(self, app, call_list=None):
        """
        Recursively detects any dependency cycles based on the specific app. A running list of
        app calls is kept and passed to each function call. If a circular dependency is detected
        an `InitialDataCircularDependency` exception will be raised. If a dependency does not exist,
        an `InitialDataMissingApp` exception will be raised.
        :param app: The name of the app in which to detect cycles. This should be the same path as defined
            in settings.INSTALLED_APPS
        :type app: str
        :param call_list: A running list of which apps will be updated in this branch of dependencies
        :type call_list: list
        """
        # start the call_list with the current app if one wasn't passed in recursively
        call_list = call_list or [app]

        # load the initial data class for the app
        try:
            initial_data_class = self.load_app(app)
        except ImproperlyConfigured:
            raise InitialDataMissingApp(dep=app)

        dependencies = initial_data_class.dependencies
        # loop through each dependency and check recursively for cycles
        for dep in dependencies:
            if dep in call_list:
                raise InitialDataCircularDependency(dep=dep, call_list=call_list)
            else:
                self.get_dependency_call_list(dep, call_list + [dep])
        call_list.extend(dependencies)

        return call_list[1:]

    def log(self, str):
        """
        Convenient way to output data and maintain coverage without having if-statements scattered throughout
        the code base with duplicate tests to test the verbose branches
        """
        if self.verbose:
            print str
