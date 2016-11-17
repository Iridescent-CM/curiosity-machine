from django.core.management.base import BaseCommand, CommandError
import inspect
from .. import fixtures

def is_module_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod

class Command(BaseCommand):

    help = 'Run fixture functions for data setup'

    def add_arguments(self, parser):
        parser.add_argument('fixture', nargs='*', type=str)

        parser.add_argument('-l', '--list',
            action='store_true',
            dest='list',
            default=False,
            help='List available fixture functions'
        )

    def get_available(self):
        return [func.__name__ for func in fixtures.__dict__.values() if is_module_function(fixtures, func)]

    def list_available(self):
        self.stdout.write("Available fixtures:")
        for item in self.get_available():
            self.stdout.write("\t%s" % item)

    def handle(self, *args, **options):
        if not options['fixture'] or options['list']:
            self.list_available()
            return

        for name in options['fixture']:
            fixture = getattr(fixtures, name)
            fixture()
            self.stdout.write('%s: OK' % name)

