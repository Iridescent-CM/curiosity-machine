from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from .signrequest import send_underage_consent_form as _send_underage_consent_form
import django_rq
import re


default_app_config = 'hellosign.apps.HellosignConfig'


def send_underage_consent_form(sender):
    django_rq.enqueue(_send_underage_consent_form, sender)

class ConsentTemplate:
    def __init__(self, id, *args, **kwargs):
        self.id = id
        self.name = self.find_name(id)

    def find_name(self, id):
        for attr in dir(settings):
            match = re.match(r'HELLOSIGN_TEMPLATE_(.*)_ID', attr)
            if match and getattr(settings, attr) == id:
                return match[1]
        raise ImproperlyConfigured("Unable to find Hellosign template configuration with ID=%s" % id)

    def __getattr__(self, attrname):
        return getattr(settings, "HELLOSIGN_TEMPLATE_%s_%s" % (self.name, attrname.upper()))
