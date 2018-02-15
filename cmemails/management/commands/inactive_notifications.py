from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from profiles.models import UserExtra
from ... import send

class Command(BaseCommand):
    help = 'Send out email notifications for inactive users'

    def handle(self, *args, **options):
        # TODO: these might be better as a bulk sends

        for extra in (
            UserExtra.students
            .inactive_since(settings.EMAIL_INACTIVE_DAYS_STUDENT)
            .filter(last_inactive_email_sent_on=None)
        ):
            send(template_name='student-inactive-2-weeks', to=extra.user, merge_vars={
                'studentname': extra.user.username
            })
            extra.last_inactive_email_sent_on = now()
            extra.save(update_fields=['last_inactive_email_sent_on'])

        for extra in (
            UserExtra.families
            .inactive_since(settings.EMAIL_INACTIVE_DAYS_FAMILY)
            .filter(last_inactive_email_sent_on=None)
        ):
            send(template_name='family-account-inactive-2-weeks', to=extra.user, merge_vars={
                'username': extra.user.username
            })
            extra.last_inactive_email_sent_on = now()
            extra.save(update_fields=['last_inactive_email_sent_on'])