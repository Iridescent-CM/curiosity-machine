from django.core.management.base import BaseCommand, CommandError
from profiles.models import Profile
from ... import send

class Command(BaseCommand):
    help = 'Send out email notifications for inactive users'

    def handle(self, *args, **options):
        profiles = Profile.inactive_students()
        for profile in profiles:
            # TODO: this might be better as a bulk send
            send(template_name='student-inactive-2-weeks', to=profile.user, merge_vars={
                'studentname': profile.user.username
            })
            profile.update_inactive_email_sent_on_and_save()