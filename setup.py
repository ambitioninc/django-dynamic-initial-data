# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'dynamic_initial_data/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-dynamic-initial-data',
    version=get_version(),
    description='Dynamic initial data fixtures for Django apps',
    long_description=open('README.md').read(),
    url='https://github.com/ambitioninc/django-dynamic-initial-data',
    author='',
    author_email='opensource@ambition.com',
    keywords='Django fixtures',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    license='MIT',
    install_requires=[
        'Django>=1.11',
        'django-manager-utils>=1.0.0',
    ],
    tests_require=[
        'psycopg2',
        'django-dynamic-fixture',
        'django-nose>=1.4',
        'freezegun',
        'mock',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
)
