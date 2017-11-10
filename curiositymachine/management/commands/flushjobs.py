from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import django_rq

class Command(BaseCommand):
    help = 'Flush all scheduled jobs without executing them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry-run',
            default=False,
            help='Show scheduled jobs without actually flushing them'
        )

    def handle(self, *args, **options):
        queue = django_rq.get_queue()
        jobs = queue.get_jobs()
        for job in jobs:
            self.stdout.write('%s\n-----' % job)

        if len(jobs) > 0:
            self.stdout.write('Flushing %d jobs.' % len(jobs))
            if not options['dry-run']:
                queue.empty()
        else:
            self.stdout.write('0 jobs scheduled.')
