import mandrill
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_template(template_name=None, to=[], cc=[], **kwargs):
    if not isinstance(to, (list, tuple)):
        to = [to]
    if not isinstance(cc, (list, tuple)):
        cc = [cc]

    recipients = [
        {
            "email": recipient.email,
            "name": recipient.username,
            "type": "to"
        }
        for recipient in to
        if recipient.email
    ]

    non_recipients = [recipient.username for recipient in to if not recipient.email]
    if non_recipients:
        logger.info("Not sending %s to user(s) %s; no email address(es)" % (template_name, ', '.join(non_recipients)))


    if recipients:
        recipients += [
            {
                "email": recipient,
                "type": "cc"
            }
            for recipient in cc
        ]

        mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)

        message = dict(settings.MANDRILL_MESSAGE_DEFAULTS, **{
          "to": recipients,
          "merge_vars": [
              #{
              #"name": "username",
              #"content": to.username
              #},
          ],
          "preserve_recipients": True
        })
        result = mandrill_client.messages.send_template(template_name=template_name, template_content=[], message=message)
