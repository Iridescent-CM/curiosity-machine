from django.conf import settings
from django.core.mail import EmailMessage
import mandrill
import logging

logger = logging.getLogger(__name__)

def deliver_email(subject, from_email, to, text_content, html_part, cc=None):
  if cc:
    print(cc)
    msg = EmailMessage(subject, '', from_email, to, cc=cc)
  else:
    msg = EmailMessage(subject, '', from_email, to)
  msg.attach(html_part)
  msg.send()

def send_mandrill_email(template_name=None, to=None):
  mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
  message = {
    "to": [{
      "email": to.email,
      "name": to.username,
      "type": "to"
    }],
    "merge": True,
    "merge_language": "handlebars",
    "global_merge_vars": [
      {
        "name": "username",
        "content": to.username
      },
      { "name": "somedict",
        "content": {"key_a": "val_a", "key_b": "val_b"}
      }
    ]
  }
  result = mandrill_client.messages.send_template(template_name=template_name, template_content=[], message=message)
  logger.info("template_name=%s to=%s result=%s" % (template_name, to, result))