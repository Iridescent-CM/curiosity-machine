from django.core.management.base import BaseCommand, CommandError
from profiles.models import Profile

class Command(BaseCommand):
    help = 'Send out email notifications for inactive users'

    def handle(self, *args, **options):
        profiles = Profile.inactive_students()
        for profile in profiles:
            profile.deliver_inactive_email()
            profile.update_inactive_email_sent_on_and_save()

        profiles = Profile.inactive_mentors()
        for profile in profiles:
            profile.deliver_encouragement_email()
            profile.update_inactive_email_sent_on_and_save()