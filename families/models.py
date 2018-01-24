from django.contrib.auth import get_user_model
from django.db import models
from enum import Enum
from images.models import Image
from locations.models import Location
from phonenumber_field.modelfields import PhoneNumberField
from profiles.models import BaseProfile

__all__ = [
    'FamilyProfile',
    'FamilyMember',
    'FamilyRole',
]

class FamilyProfile(BaseProfile):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    phone = PhoneNumberField()
    location = models.ForeignKey(Location, null=False, blank=False, on_delete=models.PROTECT)

class FamilyRole(Enum):
    parent_or_guardian = 0
    child = 1

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
        choices=[(role.value, role.name) for role in FamilyRole]
    )

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)
