from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import importlib

class Command(BaseCommand):
    help = 'Create models from factories'
    args = '<path.to.ModelFactory>'
    option_list = BaseCommand.option_list + (
        make_option(
            "-k", "--kwarg",
            action="append", dest="factory_kwargs", type="string",
            help="Keyword argument to pass to the factory; use multiple times for multiple kwargs", metavar="key=value"
        ),
        make_option(
            "-c", "--count",
            action="store", dest="count", type="int", default=1,
            help="Number of times to run factory"
        )
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Specify a factory path")
        try:
            factorypath = args[0]
            components = factorypath.split('.')
            modulepath = '.'.join(components[0:-1])
            factoryname = components[-1]
            module = __import__(modulepath, fromlist=[factoryname])
            factory = getattr(module, factoryname)
        except ImportError:
            raise CommandError("Can't import %s " % modulepath)
        except AttributeError:
            raise CommandError("Can't find %s in %s" % (factoryname, modulepath))

        kwargs = {}
        if options.get('factory_kwargs'):
            kwargs = dict([pair.split('=') for pair in options.get('factory_kwargs')])

        
        for x in range(0, options['count']):
            instance = factory(**kwargs)
            print(instance)

