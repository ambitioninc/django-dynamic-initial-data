import abc

from django.conf import settings

from initial_data.exceptions import InitialDataCircularDependency
from initial_data.utils.import_string import import_string

class BaseInitialData(object):
    dependencies = []

    @abc.abstractmethod
    def update_static(self, *args, **kwargs):
        pass


class InitialDataManager(object):
    def __init__(self):
        self.updated_apps = []

    def load_app(self, app):
        class_path = '{0}.fixtures.initial_data.InitialData'.format(app)
        print 'load', class_path
        initial_data_class = import_string(class_path)
        print initial_data_class
        if initial_data_class and issubclass(initial_data_class, BaseInitialData):
            return initial_data_class
        return None

    def update_app(self, app):
        # don't update this app if it has already been updated
        if app in self.updated_apps:
            return
        # load the app config class
        initial_data_class = self.load_app(app)
        if initial_data_class:
            # update static data
            self.detect_dependency_cycles(app)
            initial_data_class().update_static()
        # keep track that this app has been updated
        self.updated_apps.append(app)

    def update_all_apps(self):
        for app in settings.INSTALLED_APPS:
            self.update_app(app)

    def detect_dependency_cycles(self, app, call_list=None):
        call_list = call_list or [app]
        initial_data_class = self.load_app(app)
        if initial_data_class:
            dependencies = initial_data_class().dependencies
            for dep in dependencies:
                if dep in call_list:
                    raise InitialDataCircularDependency(dep=dep, call_list=call_list)
                else:
                    self.detect_dependency_cycles(dep, call_list + [dep])
            call_list += dependencies
        return call_list
