[![Build Status](https://travis-ci.org/ambitioninc/django-dynamic-initial-data.png)](https://travis-ci.org/ambitioninc/django-dynamic-initial-data)

## Django Initial Data

Django Dynamic Initial Data is a `django>=1.6` and *postgresql* only app that helps solve the problem of initializing data for apps with
dependencies and other conditional data. Rather than having static fixtures for each app, the initial data
can be created and updated dynamically. Furthermore, Django Dynamic Initial Data also handles when objects are
deleted from initial data, a feature that Django's initial data fixture system lacks.

## Table of Contents

1. [Installation] (#installation)
2. [A Brief Overview] (#a-brief-overview)
3. [Example] (#example)
4. [Handling Deletions](#handling-deletions)

## Installation
To install Django Dynamic Initial Data:

```shell
pip install django-dynamic-initial-data
```

Add Django Dynamic Initial Data to your `INSTALLED_APPS` to get started:

settings.py
```python
INSTALLED_APPS = (
    'dynamic_initial_data',
)
```

## A Brief Overview

A management command `update_initial_data` is provided which will try to update all `INSTALLED_APPS`. This
command is intended to be called as part of the deployment process of your app. Any missing dependencies
will raise an `InitialDataMissingApp` exception and any circular dependencies will raise an
`InitialDataCircularDependency` exception.

Any app needing to define initial data needs a file called `initial_data.py` inside of a `fixtures`
directory. This will look like `{app_name}/fixtures/initial_data.py`. Don't forget to include
the `__init__.py` file in the fixtures directory. `initial_data.py` must define a class `InitialData`
that inherits from `BaseInitialData`.

When apps are being initialized, each `InitialData` class is instantiated and `update_initial_data` is called.
If `update_initial_data` is not implemented, then a `NotImplementedError` will be raised.

Any dependencies should be included in a list called `dependencies`. Each dependency is a string
of the app name as defined in `INSTALLED_APPS`.

## Example:

```python
from dynamic_initial_data.base import BaseInitialData

class InitialData(BaseInitialData):
    dependencies = ['my_first_app', 'my.second.app']

    def update_initial_data(self):
        model_obj, created = TestModel.objects.upsert(int_field=5, defaults={'float_field': 2.0})

        TestModel.objects.bulk_upsert([
            TestModel(float_field=1.0, char_field='1', int_field=1),
            TestModel(float_field=2.0, char_field='2', int_field=2),
            TestModel(float_field=3.0, char_field='3', int_field=3),
        ], ['int_field'], ['char_field'])
```
In this example, the `update_initial_data` method will be called for `my_first_app` (following any dependencies first),
and then for `my.second.app`, before finally calling `update_initial_data` on this class. Again, this can be executed by calling

```
python manage.py update_initial_data
```

Similarly, to only initialize a single app, use

```
python manage.py update_initial_data --app 'app_path'
```

Documentation on using `upsert` and `bulk_upsert` can be found below:
- https://github.com/ambitioninc/django-manager-utils#upsert
- https://github.com/ambitioninc/django-manager-utils#bulk_upsert

## Handling Deletions
One difficulty when specifying initial data in Django apps is the inability to deploy initial data to your project and then subsequently remove any initial data fixtures. If one removes an object in an initial_data.json file, Django does not handle its deletion next time it is deployed, which can cause headaches with lingering objects.

Django Dynamic Initial Data fixes this problem by allowing the user to either:

1. Return all managed initial data objects as an array from the update_initial_data function.
2. Explicitly register objects for deletion with the register_for_deletion(*model_objs) method.

Note that it is up to the user to be responsible for always registering every object every time, regardless if the object was updated or created by the initial data process. Doing this allows Django Dynamic Initial Data to remove any objects that were previosly managed. For example, assume you have an InitialData class that manages two users with the user names "hello" and "world".

```python
from dynamic_initial_data.base import BaseInitialData

class InitialData(BaseInitialData):
    def update_initial_data(self):
        hello = Account.objects.get_or_create(name='hello')
        world = Account.objects.get_or_create(name='world')
        # register the accounts for deletion
        self.register_for_deletion(hello, world)
```

After this code is created, the initial data process now owns the "hello" and "world" account objects. If these objects are not registered for deletion in subsequent versions of the code, they will be deleted when the initial data process executes. For example, assume the first piece of code executed and then the user executed this piece of code:

```python
from dynamic_initial_data.base import BaseInitialData

class InitialData(BaseInitialData):
    def update_initial_data(self):
        world = Account.objects.get_or_create(name='world')
        # register the accounts for deletion
        self.register_for_deletion(world)
```

When this piece of code executes, the previous "hello" account would then be deleted since the initial data process no longer owns it. And don't worry, if it was already deleted by another process, the deletion will not throw an error.