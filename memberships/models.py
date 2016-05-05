from django.db import models
from challenges.models import Challenge
from django.contrib.auth.models import User

class Membership(models.Model):
    name = models.CharField(unique=True, max_length=255, null=False, blank=False)
    expiration = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    challenges = models.ManyToManyField(Challenge, null=True, blank=True)
    members = models.ManyToManyField(User, through='Member', through_fields=('membership', 'user'), null=True, blank=True)

class Member(models.Model):
    membership = models.ForeignKey(Membership)
    user = models.ForeignKey(User)
