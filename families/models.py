from django.db import models
from images.models import Image
from phonenumber_field.modelfields import PhoneNumberField
from profiles.models import BaseProfile

__all__ = [
    'FamilyProfile'
]

class FamilyProfile(BaseProfile):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    phone = PhoneNumberField()
