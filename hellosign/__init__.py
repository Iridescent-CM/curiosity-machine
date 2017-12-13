default_app_config = 'hellosign.apps.HellosignConfig'

import django_rq
from .signrequest import send_underage_consent_form as _send_underage_consent_form


def send_underage_consent_form(sender):
    django_rq.enqueue(_send_underage_consent_form, sender)