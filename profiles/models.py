from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile',null=True)
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.CharField(max_length=128,blank=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    occupation = models.CharField(max_length=255,blank=True)
    parent_first_name = models.CharField(max_length=64, blank=True, null=True)
    parent_last_name = models.CharField(max_length=64, blank=True, null=True)
