from django.core.management.base import BaseCommand, CommandError
from ...models import *

class Command(BaseCommand):
    help = "Initiate S3 upload job on Images"

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--all',
            action="store_true",
            dest="all",
            default=False,
            help="Start upload job for all images lacking an s3 key"
        )
        parser.add_argument(
            '-m', '--max',
            action="store",
            type=int,
            dest="max",
            default=0,
            help="Number of images to process (max)"
        )
        parser.add_argument(
            '--id',
            action="append",
            default=[],
            dest='ids',
            help='Image ids to process'
        )
        parser.add_argument(
            '-c', '--count',
            action="store_true",
            default=False,
            dest="count",
            help="Output count of images without keys"
        )

    def handle(self, *args, **options):
        if options["count"]:
            count = Image.objects.filter(key='').count()
            self.stdout.write(self.style.NOTICE("%d images without S3 keys" % count)) 
            return

        if len([key for key in ['ids', 'max', 'all'] if options[key]]) > 1:
            raise CommandError('--id, --max and --all are mutually exclusive: use only one.')

        images = []
        if options['ids']:
            images = Image.objects.filter(id__in=options['ids']).all()
        elif options['all']:
            images = Image.objects.filter(key='').all()
        elif options['max']:
            images = Image.objects.filter(key='').order_by('-id')[:options['max']]

        for image in images:
            self.stdout.write(self.style.NOTICE(image))
            image.fetch_from_source()