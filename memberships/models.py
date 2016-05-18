from django.db import models
from challenges.models import Challenge
from profiles.models import UserRole
from django.contrib.auth.models import User

class Membership(models.Model):
    name = models.CharField(unique=True, max_length=255, null=False, blank=False)
    expiration = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    challenges = models.ManyToManyField(Challenge, blank=True)
    members = models.ManyToManyField(User, through='Member', through_fields=('membership', 'user'), blank=True)

    def __str__(self):
        return self.name

class Member(models.Model):
    membership = models.ForeignKey(Membership)
    user = models.ForeignKey(User)

class MemberLimit(models.Model):
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in UserRole], default=UserRole.none.value)
    limit = models.PositiveIntegerField(null=False, blank=True, default=0)
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)
