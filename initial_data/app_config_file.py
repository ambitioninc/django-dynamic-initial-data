import abc

from django.conf import settings

from .exceptions import AppConfigCircularDependency
from .utils.import_string import import_string


class BaseAppConfig(object):
    dependencies = []

    @abc.abstractmethod
    def update_static(self, *args, **kwargs):
        pass


class AppConfigManager(object):
    def __init__(self):
        self.updated_apps = []

    def load_app(self, app):
        app_config_path = '{0}.fixtures.initial_data.AppConfig'.format(app)
        app_config_class = import_string(app_config_path)
        if app_config_class and issubclass(app_config_class, BaseAppConfig):
            return app_config_class
        return None

    def update_app(self, app):
        # don't update this app if it has already been updated
        if app in self.updated_apps:
            return
        # load the app config class
        app_config_class = self.load_app(app)
        if app_config_class:
            # update static data
            self.detect_dependency_cycles(app)
            app_config_class().update_static()
        # keep track that this app has been updated
        self.updated_apps.append(app)

    def update_all_apps(self):
        for app in settings.INSTALLED_APPS:
            self.update_app(app)

    def detect_dependency_cycles(self, app, call_list=None):
        call_list = call_list or [app]
        app_config_class = self.load_app(app)
        if app_config_class:
            dependencies = app_config_class().dependencies
            for dep in dependencies:
                if dep in call_list:
                    raise AppConfigCircularDependency(dep=dep, call_list=call_list)
                else:
                    self.detect_dependency_cycles(dep, call_list + [dep])
            call_list += dependencies
        return call_list
