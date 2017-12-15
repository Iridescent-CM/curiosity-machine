from django.db import models
from images.models import Image
from profiles.models import BaseProfile

class FamilyProfile(BaseProfile):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
