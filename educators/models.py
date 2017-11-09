from django.db import models
from images.models import Image
from profiles.models import BaseProfile

class EducatorProfile(BaseProfile):
    city = models.TextField(blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.CharField(max_length=50, null=True, blank=True)
