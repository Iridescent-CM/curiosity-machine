from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from django.db.models.signals import pre_save
from curiositymachine.helpers import random_string



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

    def __str__(self):
        return "Group={}".format(self.name)

    def __repr__(self):
        return "Group={}".format(self.name)


def create_code(sender, instance, **kwargs):
    def unique_slug(length=5, lists_num=1):
        string = random_string()
        if Group.objects.filter(code=string).exists():
            return unique_slug(length + 1, lists_num + 1)
        else:
            return string

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
