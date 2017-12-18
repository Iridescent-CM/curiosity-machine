from django.core.management.base import BaseCommand, CommandError
from profiles.models import UserExtra
from ... import send

class Command(BaseCommand):
    help = 'Send out email notifications for inactive users'

    def handle(self, *args, **options):
        extras = UserExtra.inactive_students()
        for extra in extras:
            # TODO: this might be better as a bulk send
            send(template_name='student-inactive-2-weeks', to=extra.user, merge_vars={
                'studentname': extra.user.username
            })
            extra.update_inactive_email_sent_on_and_save()