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


def get_lines(file_path):
    return open(file_path, 'r').read().split('\n')


install_requires = get_lines('requirements/requirements.txt')
tests_require = get_lines('requirements/requirements-testing.txt')


setup(
    name='django-dynamic-initial-data',
    version=get_version(),
    description='Dynamic initial data fixtures for Django apps',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ambitioninc/django-dynamic-initial-data',
    author='',
    author_email='opensource@ambition.com',
    keywords='Django fixtures',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
    ],
    license='MIT',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='run_tests.run_tests',
    include_package_data=True,
)
