from django.core.management.base import BaseCommand, CommandError
from profiles.models import Profile
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Reset all users to have now as the "last active on" value'

    def handle(self, *args, **options):
        Profile.objects.all().update(last_active_on=now())