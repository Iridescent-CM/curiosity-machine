from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.db import models
from enumfields import Enum, EnumIntegerField
from pydoc import locate
import re
import uuid

class ConsentTemplate:
    prefix = "HELLOSIGN_TEMPLATE_"
    defaults = {
        'BYPASS_API': False,
        'ACTIVE': False,
    }
    id = None

    def __new__(cls, *args, **kwargs):
        if cls is ConsentTemplate:
            raise TypeError("ConsentTemplate may not be instantiated directly")
        return object.__new__(cls)

    def __init__(self, id=None, *args, **kwargs):
        if self.id and id and not self.id == id:
            raise ValueError("Constructor cannot take different id than id already assigned to the class")
        self.id = self.id or id
        self.name = self.find_name(self.id)

    def __getattr__(self, attrname):
        return self.find_setting(self.name, attrname)

    @classmethod
    def lookup_instance(cls, id):
        name = cls.find_name(id)
        try:
            subclass = cls.find_setting(name, 'CLASS')
            return locate(subclass)(id)
        except AttributeError:
            return GenericConsentTemplate(id)

    @classmethod
    def find_name(cls, id):
        for attr in dir(settings):
            match = re.match(r'%s(.*)_ID' % cls.prefix, attr)
            if match and getattr(settings, attr) == id:
                return match[1]
        raise ImproperlyConfigured("Unable to find Hellosign template configuration with ID=%s" % id)

    @classmethod
    def find_setting(cls, templatename, settingname):
        settingname = settingname.upper()
        fullname = "%s%s_%s" % (cls.prefix, templatename.upper(), settingname)
        if settingname in cls.defaults:
            return getattr(settings, fullname, cls.defaults[settingname])
        return getattr(settings, fullname)

    def get_custom_fields(self, signature):
        raise NotImplementedError("Subclass must implement get_custom_fields")

    def signature(self, user):
        from . import jobs
        signature, created = Signature.objects.get_or_create(user=user, template_id=self.id)
        if created and not self.bypass_api:
            jobs.request_signature(signature.id)
        return signature

class GenericConsentTemplate(ConsentTemplate):

    def get_custom_fields(self, signature):
        fields = {}
        if hasattr(self, "email_id"):
            fields[self.email_id] = signature.user.email
        if hasattr(self, "username_id"):
            fields[self.username_id] = signature.user.username
        if hasattr(self, "birthday_id"):
            fields[self.birthday_id] = signature.user.studentprofile.birthday.strftime('%b %d, %Y')
        return fields

class FamilyConsentTemplate(ConsentTemplate):
    id = settings.AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID

    def get_custom_fields(self, signature):
        fields = super().get_custom_fields(signature)
        # TODO: add extra fields here
        return fields

class StudentConsentTemplate(GenericConsentTemplate):
    id = settings.HELLOSIGN_TEMPLATE_STUDENT_CONSENT_ID

class SignatureStatus(Enum):
    UNSIGNED = 0
    SIGNED = 1

class Signature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_id = models.CharField(max_length=40, null=False, blank=False)
    signature_request_id = models.CharField(max_length=50, null=True, blank=True)
    signature_id = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(get_user_model(), null=False, blank=False)
    status = EnumIntegerField(SignatureStatus, default=SignatureStatus.UNSIGNED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def template(self):
        return ConsentTemplate.lookup_instance(self.template_id)

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
        return self.template.get_custom_fields(self)

    def get_metadata(self):
        return {
            "template_id": self.template_id,
            "signature_id": self.id,
            "user_id": self.user.id,
            "environment_name": settings.HELLOSIGN_ENVIRONMENT_NAME
        }

    def __str__(self):
        return "Signature: id={}, template_id={}, user_id={}, status={}".format(
            self.id,
            self.template_id,
            self.user_id,
            self.status.name
        )
