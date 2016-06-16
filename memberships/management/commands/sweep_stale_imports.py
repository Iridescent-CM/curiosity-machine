from django.core.management.base import BaseCommand
from memberships.models import MemberImport

class Command(BaseCommand):
    help = 'Delete stale member import objects'

    def handle(self, *args, **options):
        self.stdout.write("Sweeping imports older than %s" % MemberImport.stale_objects.threshold)
        count = MemberImport.stale_objects.count()
        MemberImport.stale_objects.all().delete()
        self.stdout.write("%d imports deleted" % count)
