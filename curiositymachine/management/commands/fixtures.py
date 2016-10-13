from django.core.management.base import BaseCommand, CommandError
import inspect
from . import _fixtures

def is_module_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('fixture', nargs='*', type=str)

    def handle(self, *args, **options):
        if not options['fixture']:
            available = [func.__name__ for func in _fixtures.__dict__.values() if is_module_function(_fixtures, func)] 
            self.stdout.write("Available fixtures:")
            for item in available:
                self.stdout.write("\t%s" % item)
            return

        for name in options['fixture']:
            fixture = getattr(_fixtures, name)
            fixture()
            self.stdout.write('%s: OK' % name)

