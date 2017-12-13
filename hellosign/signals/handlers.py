from curiositymachine import signals
from django.dispatch import receiver
from hellosign import send_underage_consent_form

from curiositymachine import signals
from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from cmemails import send, subscribe
from cmemails.mandrill import url_for_template
from challenges.models import Stage
import urllib.parse
import re


@receiver(signals.created_profile)
def send_consent_email(sender, **kwargs):
    if sender.extra.send_welcome:
        if sender.extra.is_student:
            if sender.studentprofile.is_underage():
                # For underage users we will be using
                # the Hellosign e-ign option, not email.
                send_underage_consent_form(sender)
