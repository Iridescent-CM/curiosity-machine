from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.db import models
from enumfields import Enum, EnumIntegerField
import uuid

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
        return [
            {
                "name": self.user.username,
                "email_address": self.user.email,
                "role_name": "Parent or guardian"
            }
        ]

    def get_subject(self):
        subject = render_to_string(
            '%s_subject.txt' % self.template.name.lower(),
            {
                "signature": self
            }
        )
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        return subject

    def get_message(self):
        body = render_to_string(
            '%s_message.txt' % self.template.name.lower(),
            {
                "signature": self
            }
        )
        return body

    def get_metadata(self):
        return {
            "template_id": self.template_id,
            "signature_id": self.id,
            "user_id": self.user.id,
            "production_mode": settings.HELLOSIGN_PRODUCTION_MODE
        }
