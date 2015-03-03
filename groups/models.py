import time
import django_rq
from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from django.db.models.signals import pre_save
from curiositymachine.helpers import random_string
from cmemails import deliver_email
from django.conf import settings
from django_simple_redis import redis
from uuid import uuid4


INVITATIONS_NS = "curiositymachine:invitations:{group_id}:{token}"
EXPIRY = int(settings.GROUP_INVITATION_INACTIVE_DAYS) * 1000 * 1000

class Role(Enum):
    educator = 0
    student = 1

class Group(models.Model):
    name = models.CharField('name', max_length=80, null=True, blank=False)
    code = models.CharField('code', max_length=20, unique=True, null=True, blank=False)
    members = models.ManyToManyField(User, through='Membership', through_fields=('group', 'user'), related_name="cm_groups")

    def educators(self):
        return User.objects.filter(cm_groups=self, memberships__role=Role.educator.value)

    def students(self): 
        return User.objects.filter(cm_groups=self, memberships__role=Role.student.value).prefetch_related('progresses__challenge')

    def add_student(self, user):
        if not Membership.objects.filter(group=self, user=user, role=Role.student.value).exists():
            Membership.objects.create(group=self, user=user, role=Role.student.value)
            return True
        return False

    def add_educator(self, user):
        if not Membership.objects.filter(group=self, user=user, role=Role.educator.value).exists():
            Membership.objects.create(group=self, user=user, role=Role.educator.value)
            return True
        return False

    def delete_student(self, user):
        if Membership.objects.filter(group=self, user=user, role=Role.student.value).exists():
            Membership.objects.get(group=self, user=user, role=Role.student.value).delete()
            return True
        return False

    def invite_student(self, user):
        token = str(uuid4())
        redis.setex(INVITATIONS_NS.format(group_id=str(self.id), token=token), user.id, EXPIRY)
        #send an email
        deliver_email('group_invite', user.profile, group=self, token=token)
        return True

    def accept_invitation(self, token):
        user_id = redis.get(INVITATIONS_NS.format(group_id=str(self.id), token=token))
        user = User.objects.get(pk=int(user_id))
        self.add_student(user)
        return user

    def __str__(self):
        return "Group={}".format(self.name)

    def __repr__(self):
        return "Group={}".format(self.name)


def create_code(sender, instance, **kwargs):
    def unique_slug(length=5):
        string = random_string(length)
        if Group.objects.filter(code=string).exists():
            return unique_slug(length + 1)
        else:
            return string

    #check that this model hasn't been created yet
    if not instance.id:
        instance.code = unique_slug()

pre_save.connect(create_code, sender=Group)

class Membership(models.Model):
    group = models.ForeignKey(Group, related_name="memberships")
    user = models.ForeignKey(User, related_name="memberships")
    role = models.SmallIntegerField(choices=[(role.value, role.name.capitalize()) for role in Role], default=Role.educator.value)

    def __str__(self):
        return "Group={} User={}".format(self.group, self.user)

    def __repr__(self):
        return "Group={} User={}".format(self.group, self.user)
