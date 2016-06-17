from django.core.management.base import BaseCommand
from optparse import make_option
from memberships.models import MemberImport

class Command(BaseCommand):
    help = 'Delete stale member import objects'
    option_list = BaseCommand.option_list + (
        make_option(
            "-a", "--age",
            action="store",
            dest="age",
            type="int",
            help="Set the age in days for staleness"
        ),
    )

    def handle(self, *args, **options):
        age = options.get("age", None)
        self.stdout.write("Sweeping imports older than %s" % MemberImport.stale_objects.threshold(age))

        count = MemberImport.stale_objects.older_than(age).count()
        MemberImport.stale_objects.older_than(age).all().delete()
        self.stdout.write("%d imports deleted" % count)
