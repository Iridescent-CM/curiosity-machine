from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from .api import HelloSign
from .signrequest import send_underage_consent_form as _send_underage_consent_form
import django_rq
import re


default_app_config = 'hellosign.apps.HellosignConfig'


def send_underage_consent_form(sender):
    django_rq.enqueue(_send_underage_consent_form, sender)

class ConsentTemplate:
    prefix = "HELLOSIGN_TEMPLATE_"
    defaults = {
        'BYPASS_API': False
    }

    def __init__(self, id, *args, **kwargs):
        self.id = id
        self.name = self.find_name(id)

    def find_name(self, id):
        for attr in dir(settings):
            match = re.match(r'%s(.*)_ID' % self.prefix, attr)
            if match and getattr(settings, attr) == id:
                return match[1]
        raise ImproperlyConfigured("Unable to find Hellosign template configuration with ID=%s" % id)

    def __getattr__(self, attrname):
        attrname = attrname.upper()
        settingname = "%s%s_%s" % (self.prefix, self.name, attrname)
        if attrname in self.defaults:
            return getattr(settings, settingname, self.defaults[attrname])
        return getattr(settings, settingname)

    def signature(self, user):
        from .models import Signature
        signature, created = Signature.objects.get_or_create(user=user, template_id=self.id)
        if created and not self.bypass_api:
            HelloSign().request_signature(signature)
        return signature
