import os

from django.core.management.base import BaseCommand
from django.conf import settings


APP_PATH = os.path.join(settings.PROJECT_PATH, 'apps')


class Command(BaseCommand):
    help = 'Detect any dependency cycles in the app_config process'

    def handle(self, *args, **options):
        pass
