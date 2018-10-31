from curiositymachine import signals
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now
from enum import Enum
from hellosign.models import FamilyConsentTemplate
from images.models import Image
from locations.models import Location
from phonenumber_field.modelfields import PhoneNumberField
from profiles.models import BaseProfile
from surveys import get_survey

__all__ = [
    'FamilyProfile',
    'FamilyMember',
    'FamilyRole',
    'AwardForceIntegration',
]

class FamilyProfile(BaseProfile):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    phone = PhoneNumberField(null=True, blank=True)
    location = models.ForeignKey(Location, null=False, blank=False, on_delete=models.PROTECT)
    welcomed = models.DateTimeField(null=True, blank=True)
    members_confirmed = models.BooleanField(default=False)

    @cached_property
    def full_access(self):
        return self.check_full_access()

    def check_full_access(self):
        presurvey = get_survey(settings.AICHALLENGE_FAMILY_PRE_SURVEY_ID)
        if presurvey.active:
            response = presurvey.response(self.user)
            if not response.completed:
                return False

        consent = FamilyConsentTemplate(settings.AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID)
        if consent.active:
            signature = consent.signature(self.user)
            if not signature.signed:
                return False

        return True

    def check_welcome(self):
        if self.check_full_access() and not self.welcomed:
            signals.account_activation_confirmed.send(sender=self.user)
            self.welcomed = now()
            self.save(update_fields=['welcomed'])

class FamilyRole(Enum):
    parent_or_guardian = 0
    child = 1

    def display(self):
        return self.name.replace("_", " ").capitalize()

class FamilyMember(models.Model):
    account = models.ForeignKey(
        get_user_model(),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField(blank=True, null=True)
    family_role = models.SmallIntegerField(
        null=False,
        blank=False,
        choices=[(None, 'Select role...')] + [(role.value, role.display()) for role in FamilyRole]
    )

    @property
    def family_role_display(self):
        return FamilyRole(self.family_role).display()

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

class AwardForceIntegration(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    slug = models.CharField(max_length=16, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
