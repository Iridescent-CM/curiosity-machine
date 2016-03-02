from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
from challenges.models import Example
import mandrill

class Command(BaseCommand):
    help = 'Send out email notification for pending examples'

    def handle(self, *args, **options):
        count = Example.objects.status(pending=True).count()
        if count > 0:

            recipients = [
                {
                    "email": recipient,
                    "type": "to"
                }
                for recipient in settings.NOTIFICATION_RECIPIENTS
            ]

            content = render_to_string("cmemails/admin/pending_examples.html", {
                "count": count,
                "site_url": settings.SITE_URL
            })

            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            message = dict(settings.MANDRILL_MESSAGE_DEFAULTS, **{
              "to": recipients,
              "subject": "%d pending example(s)" % count,
              "from_email": settings.DEFAULT_FROM_EMAIL,
              "html": content,
              "preserve_recipients": True,
              "track_opens": False,
              "track_clicks": False
            })
            result = mandrill_client.messages.send(message=message)
