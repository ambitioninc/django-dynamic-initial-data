import os

from django.core.management.base import BaseCommand
from django.conf import settings


APP_PATH = os.path.join(settings.PROJECT_PATH, 'apps')


class Command(BaseCommand):
    help = 'Detect any dependency cycles in the initial_data process'

    def handle(self, *args, **options):
        pass
