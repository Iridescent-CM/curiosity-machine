default_app_config = 'cmemails.apps.CMEmailsConfig'

from .mailer import deliver_email # deprecated

import django_rq
from .mandrill import send_template
from .mailchimp import subscribe as _subscribe

def send(**kwargs):
    django_rq.enqueue(send_template, **kwargs)

def subscribe(*args, **kwargs):
    django_rq.enqueue(_subscribe, *args, **kwargs)
