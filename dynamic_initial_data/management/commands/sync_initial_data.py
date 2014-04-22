from optparse import make_option

from django.core.management.base import BaseCommand

from dynamic_initial_data.base import InitialDataUpdater


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--verbose', action='store_true', dest='verbose', default=False,
            help='Determines if we should display which apps are being updated'
        ),)

    help = 'Call the AppInit.update command for all apps'

    def handle(self, *args, **options):
        manager = InitialDataUpdater(options)
        manager.update_all_apps()
