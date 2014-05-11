import os

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """
    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or Nonet
        circle_ci = os.environ.get('CIRCLECI', None)
        if circle_ci is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ambition_dev',
                'USER': 'ambition_dev',
                'PASSWORD': 'ambition_dev',
                'HOST': 'localhost'
            }
        else:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'circle_test',
                'USER': 'ubuntu',
                'PASSWORD': ''
            }

        settings.configure(
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.admin',
                'south',
                'dynamic_initial_data',
                'dynamic_initial_data.tests',
            ),
            ROOT_URLCONF='dynamic_initial_data.urls',
            DEBUG=False,
            DDF_FILL_NULLABLE_FIELDS=False,
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
        )
