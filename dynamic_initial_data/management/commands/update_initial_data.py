from django.core.management.base import BaseCommand

from dynamic_initial_data.base import InitialDataUpdater


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose', action='store_true', dest='verbose', default=False,
            help='Determines if we should display which apps are being updated'
        )
        parser.add_argument(
            '--app', dest='app', default=None, help='Updates a single app'
        )

    help = 'Call the InitialData.update_initial_data command for all apps. Use --app to update only one app.'

    def handle(self, *args, **options):
        updater = InitialDataUpdater(options)
        if options['app']:
            updater.update_app(options['app'])
        else:
            updater.update_all_apps()
