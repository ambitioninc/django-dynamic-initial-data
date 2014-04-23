from django.conf import settings

from dynamic_initial_data.exceptions import InitialDataCircularDependency, InitialDataMissingApp
from dynamic_initial_data.utils.import_string import import_string


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
        options = options or {}
        self.verbose = options.get('verbose', False)
        self.updated_apps = set()
        self.loaded_apps = {}

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
        initial_data_class = import_string(self.get_class_path(app))
        if initial_data_class and issubclass(initial_data_class, BaseInitialData):
            self.log('Loaded app {0}'.format(app))
            self.loaded_apps[app] = initial_data_class
        return self.loaded_apps[app]

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
        initial_data_class = self.load_app(app)
        if initial_data_class:
            self.log('Checking dependencies for {0}'.format(app))

            # get dependency list
            dependencies = self.get_dependency_call_list(app)

            # update initial data of dependencies
            for dependency in dependencies:
                self.update_app(dependency)

            self.log('Updating app {0}'.format(app))

            initial_data_class().update_initial_data()
            # keep track that this app has been updated
            self.updated_apps.add(app)

    def update_all_apps(self):
        """
        Loops through all app names contained in settings.INSTALLED_APPS and calls `update_app`
        on each one.
        """
        for app in settings.INSTALLED_APPS:
            self.update_app(app)

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
        initial_data_class = self.load_app(app)
        if initial_data_class:
            dependencies = initial_data_class.dependencies
            # loop through each dependency and check recursively for cycles
            for dep in dependencies:
                if dep in call_list:
                    raise InitialDataCircularDependency(dep=dep, call_list=call_list)
                else:
                    self.get_dependency_call_list(dep, call_list + [dep])
            call_list.extend(dependencies)
        else:
            raise InitialDataMissingApp(dep=app)
        return call_list[1:]

    def log(self, str):
        """
        Convenient way to output data and maintain coverage without having if-statements scattered throughout
        the code base with duplicate tests to test the verbose branches
        """
        if self.verbose:
            print str
