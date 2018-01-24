from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.db import models
from enumfields import Enum, EnumIntegerField
import re
import uuid

class ConsentTemplate:
    prefix = "HELLOSIGN_TEMPLATE_"
    defaults = {
        'BYPASS_API': False,
        'ACTIVE': False,
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
        from . import jobs
        signature, created = Signature.objects.get_or_create(user=user, template_id=self.id)
        if created and not self.bypass_api:
            jobs.request_signature(signature.id)
        return signature

class SignatureStatus(Enum):
    UNSIGNED = 0
    SIGNED = 1

class Signature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_id = models.CharField(max_length=40, null=False, blank=False)
    user = models.ForeignKey(get_user_model(), null=False, blank=False)
    status = EnumIntegerField(SignatureStatus, default=SignatureStatus.UNSIGNED)

    @property
    def template(self):
        return ConsentTemplate(self.template_id)

    def __getattr__(self, name):
        # treat status names like boolean attributes
        try:
            return self.status == SignatureStatus[name.upper()]
        except KeyError:
            pass

        # okay, there's no attribute by that name
        raise AttributeError("'Signature' object has no attribute '%s'" % name)

    def get_signers(self):
        if hasattr(self.template, "signer_role"):
            role = self.template.signer_role
        else:
            role = "Parent"
        return [
            {
                "name": self.user.username,
                "email_address": self.user.email,
                "role_name": role
            }
        ]

    def get_subject(self):
        subject = render_to_string(
            'hellosign/emails/%s_subject.txt' % self.template.name.lower(),
            {
                "signature": self
            }
        )
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        return subject

    def get_message(self):
        body = render_to_string(
            'hellosign/emails/%s_message.txt' % self.template.name.lower(),
            {
                "signature": self
            }
        )
        return body

    def get_custom_fields(self):
        fields = {}
        if hasattr(self.template, "email_id"):
            fields[self.template.email_id] = self.user.email
        if hasattr(self.template, "username_id"):
            fields[self.template.username_id] = self.user.username
        if hasattr(self.template, "birthday_id"):
            fields[self.template.birthday_id] = self.user.studentprofile.birthday.strftime('%b %d, %Y')
        return [fields]

    def get_metadata(self):
        return {
            "template_id": self.template_id,
            "signature_id": self.id,
            "user_id": self.user.id,
            "production_mode": settings.HELLOSIGN_PRODUCTION_MODE
        }

    def __str__(self):
        return "Signature: id={}, template_id={}, user_id={}, status={}".format(
            self.id,
            self.template_id,
            self.user_id,
            self.status.name
        )
