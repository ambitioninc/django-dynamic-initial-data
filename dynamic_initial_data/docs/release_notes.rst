Release Notes
=============

v3.0.0
------
* Support django 5.2 and 6.0, python 3.10 - 3.14
* Drop support for python < 3.10 and django < 5.2
* Replace django-nose with Django's ``DiscoverRunner``
* Set ``USE_TZ=False`` explicitly in the test settings (django 5.0 flipped the
  default to True)
* Replace ``assertEquals`` (removed in python 3.12) with ``assertEqual``

v2.2.1
------
* Fix manifest

v2.2.0
------
* Add support for django 3.2, 4.0, 4.1, 4.2
* Add support for python 3.8, 3.9
* Remove support for django 2.0, 2.1, 2.2, 3.0, 3.1
* Remove support for python 3.6

v2.1.0
------
* Python 3.7
* Django 2.1
* Django 2.2

v2.0.0
------
* Drop Django 1.10 support
* Drop Django 1.11 support
* Add Django 2.1 support
* Drop python 2.7 support
* Drop python 3.4 support
* Drop python 3.5 support

v1.1.0
------
* Add tox to support more versions

v1.0.0
------
* Drop Django 1.9 support
* Drop Django 1.10 support
* Add Django 2.0 support
* Drop python 2.7 support
* Drop python 3.4 support

v0.8.0
------
* Add python 3.6 support
* Drop Django 1.8 support
* Add Django 1.10 support
* Add Django 1.11 support
