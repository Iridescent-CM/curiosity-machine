from django.db import models
from django.urls import reverse
from profiles.models import BaseProfile

class StudentProfile(BaseProfile):
    birthday = models.DateField(blank=True,null=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
