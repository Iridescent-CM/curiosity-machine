from django.core.management.base import BaseCommand
from django.utils.timezone import now
from memberships.models import Membership

class Command(BaseCommand):
    help = 'Deactivate expired memberships'

    def handle(self, *args, **options):
        today = now().date()
        self.stdout.write("Deactivating expired memberships as of {:%Y-%m-%d}".format(today))

        count = Membership.objects.expired(expiration=today).exclude(is_active=False).update(is_active=False)
        self.stdout.write("%d memberships deactivated" % count)
