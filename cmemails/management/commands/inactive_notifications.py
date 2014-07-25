from django.core.management.base import BaseCommand, CommandError
from profiles.models import Profile

class Command(BaseCommand):
    help = 'Send out email notifications for inactive users'

    def handle(self, *args, **options):
        profiles = Profile.inactive_users()
        for profile in profiles:
            profile.deliver_inactive_email()