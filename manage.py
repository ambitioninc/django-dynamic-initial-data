#!/usr/bin/env python
import sys
from settings import configure_settings

import warnings
from django.utils.deprecation import RemovedInNextVersionWarning
warnings.filterwarnings('always', category=RemovedInNextVersionWarning)
warnings.filterwarnings('always', category=DeprecationWarning)
warnings.filterwarnings('always', category=PendingDeprecationWarning)


def main():
    """Run administrative tasks."""
    configure_settings()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import Django. Are you sure it is installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
