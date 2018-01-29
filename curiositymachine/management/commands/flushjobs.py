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
        parser.add_argument(
            '--failed',
            action='store_true',
            dest='failed',
            default=False,
            help='Use failed queue, not default queue'
        )
        parser.add_argument(
            '--id',
            action='append',
            dest='ids',
            default=[],
            help='ID(s) of job(s) to remove, if not flushing all'
        )

    def handle(self, *args, **options):
        queue = None
        jobs = []

        if options['failed']:
            queue = django_rq.get_failed_queue()
        else:
            queue = django_rq.get_queue()

        if options['ids']:
            for id in options['ids']:
                jobs.append(queue.fetch_job(id))
        else:
            jobs = queue.get_jobs()

        for job in jobs:
            self.stdout.write('%s\n-----' % job)

        if len(jobs) > 0:
            self.stdout.write('Flushing %d jobs.' % len(jobs))
            if not options['dry-run']:
                for job in jobs:
                    queue.remove(job)
        else:
            self.stdout.write('0 jobs scheduled.')
