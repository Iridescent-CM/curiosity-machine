from datetime import date
from django.db import models
from django.urls import reverse
from images.models import Image
from profiles.models import BaseProfile

class StudentProfile(BaseProfile):
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    city = models.TextField(blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    full_access = models.BooleanField(default=False)
