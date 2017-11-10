from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings
import redis as r

class Command(BaseCommand):
    help = 'Flush Redis keys in db'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry-run',
            default=False,
            help='Show keys without actually flushing them'
        )

    def handle(self, *args, **options):
        redis = r.from_url(settings.REDIS_URL)
        keys = redis.keys()
        for key in keys:
            self.stdout.write(str(key, 'utf-8'))
        if len(keys) > 0:
            self.stdout.write('Flushing %d keys.' % len(keys))
            if not options['dry-run']:
                redis.flushdb()
        else:
            self.stdout.write('0 keys.')