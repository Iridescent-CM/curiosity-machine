import mandrill
import logging
import urllib.parse
import re
from django.conf import settings

logger = logging.getLogger(__name__)

def url_for_template(path):
    # mailchimp/mandrill insists on adding http:// to button urls coming from variables
    return re.sub(r'.*://', '', urllib.parse.urljoin(settings.SITE_URL, path))

def send_template(template_name, to=[], cc=[], merge_vars={}, **kwargs):
    template_name = settings.MANDRILL_TEMPLATE_PREFIX + template_name

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
          "global_merge_vars": [{"name": k, "content": v} for k, v in merge_vars.items()],
          "preserve_recipients": True
        })
        results = mandrill_client.messages.send_template(template_name=template_name, template_content=[], message=message)

        unsent_results = [result for result in results if result['status'] != "sent"]
        for result in unsent_results:
            logger.warning(
                "Unsent message, recipient=%s status=%s reason=%s",
                result['email'],
                result['status'],
                result['reject_reason']
            )
