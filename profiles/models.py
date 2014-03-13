from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile',null=True)
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    location = models.CharField(max_length=128,blank=True)
    occupation = models.CharField(max_length=255,blank=True)
