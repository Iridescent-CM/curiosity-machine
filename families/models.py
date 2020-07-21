from . import *
from curiositymachine import signals
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now
from enum import Enum
from images.models import Image
from locations.models import Location
from profiles.models import BaseProfile
from surveys import get_survey

__all__ = [
    'FamilyProfile',
    'FamilyMember',
    'FamilyRole',
    'AwardForceIntegration',
    'PermissionSlip',
]

class FamilyProfile(BaseProfile):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, null=False, blank=False, on_delete=models.PROTECT)
    welcomed = models.DateTimeField(null=True, blank=True)
    members_confirmed = models.BooleanField(default=False)

    @cached_property
    def full_access(self):
        return self.check_full_access()

    def check_full_access(self):
        return (
            (self.presurvey_not_required or self.presurvey_completed) and
            self.permission_slip_signed
        )

    @property
    def surveys_required(self):
        return self.location.country in PRESURVEY_COUNTRIES

    @property
    def presurvey_not_required(self):
        return not self.surveys_required

    @property
    def presurvey_completed(self):
        presurvey = get_survey('FAMILY_PRE')
        if presurvey.active:
            response = presurvey.response(self.user)
            if not response.completed:
                return False

        return True

    @property
    def permission_slip_signed(self):
        return PermissionSlip.objects.filter(account=self.user).exists()

    def check_welcome(self):
        if self.check_full_access() and not self.welcomed:
            signals.account_activation_confirmed.send(sender=self.user)
            self.welcomed = now()
            self.save(update_fields=['welcomed'])

    def family_size(self):
        return self.user.familymember_set.count()

    def parent_guardian_first_names(self):
        parent_or_guardians = self.user.familymember_set.filter(family_role=FamilyRole.parent_or_guardian.value)
        first_names = [pog.first_name for pog in parent_or_guardians]
        return ", ".join(sorted(first_names))

    def children_first_names(self):
        children = self.user.familymember_set.filter(family_role=FamilyRole.child.value)
        first_names = [child.first_name for child in children]
        return ", ".join(sorted(first_names))

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
    last_used = models.DateTimeField(auto_now=True)

class PermissionSlip(models.Model):
    signature = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return "PermissionSlip: id=%s account=%s" % (self.id, self.account)
