import time
from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save, post_delete
from curiositymachine.helpers import random_string
from cmemails import deliver_email
from django.conf import settings
from django_simple_redis import redis
from uuid import uuid4
from django.utils.timezone import now

class Role(Enum):
    owner = 0
    member = 1

class Group(models.Model):
    name = models.CharField('name', max_length=80, null=True, blank=False)
    code = models.CharField('code', max_length=20, unique=True, null=True, blank=False)
    member_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', through_fields=('group', 'user'), related_name="cm_groups")
    invited_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Invitation', through_fields=('group', 'user'), related_name="cm_group_invites")
    created = models.DateTimeField(default=now)

    def owners(self):
        return get_user_model().objects.filter(cm_groups=self, memberships__role=Role.owner.value)

    def members(self):
        return get_user_model().objects.filter(cm_groups=self, memberships__role=Role.member.value).prefetch_related('progresses__challenge')

    def add_member(self, user):
        if not Membership.objects.filter(group=self, user=user, role=Role.member.value).exists():
            Membership.objects.create(group=self, user=user, role=Role.member.value)
            return True
        return False

    def add_owner(self, user):
        if not Membership.objects.filter(group=self, user=user, role=Role.owner.value).exists():
            Membership.objects.create(group=self, user=user, role=Role.owner.value)
            return True
        return False

    def delete_owner(self, user):
        if Membership.objects.filter(group=self, user=user, role=Role.owner.value).exists():
            Membership.objects.get(group=self, user=user, role=Role.owner.value).delete()
            return True
        return False

    def delete_member(self, user):
        if Membership.objects.filter(group=self, user=user, role=Role.member.value).exists():
            Membership.objects.get(group=self, user=user, role=Role.member.value).delete()
            return True
        return False

    def invite_member(self, user):
        if not self.member_users.filter(pk=user.id).exists():
            if Invitation.objects.filter(group=self, user=user).count() < 1:
                invitation = Invitation.objects.create(group=self, user=user)
            else:
                deliver_email('group_invite', user.profile, group=self)

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

def delete_invitations_and_members(sender, instance, **kwargs):
    for model_klass in [Membership, Invitation]:
        model_klass.objects.filter(group=instance).delete()

post_delete.connect(delete_invitations_and_members, sender=Group)

class Membership(models.Model):
    group = models.ForeignKey(Group, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memberships")
    role = models.SmallIntegerField(choices=[(role.value, role.name.capitalize()) for role in Role], default=Role.owner.value)

    def __str__(self):
        return "Group={} User={}".format(self.group, self.user)

    def __repr__(self):
        return "Group={} User={}".format(self.group, self.user)

    @classmethod
    def user_owns_group(cls, user, group_id):
        return cls.objects.filter(
            group__id=group_id,
            user=user,
            role=Role.owner.value
        ).exists()

    @classmethod
    def users_share_any_group(cls, username1, role1, username2, role2):
        return cls.objects.filter(
            user__username=username1, role=role1.value,
            group__memberships__user__username=username2,
            group__memberships__role=role2.value
        ).exists()

def delete_when_group_is_orphaned(sender, instance, **kwargs):
    group = Group.objects.filter(id=instance.group_id).first()
    if group and len(group.owners()) < 1:
        group.delete()

post_delete.connect(delete_when_group_is_orphaned, sender=Membership)

class Invitation(models.Model):
    group = models.ForeignKey(Group, related_name="group_invitations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_invitations")

    class Meta:
        unique_together = ('group', 'user')

    def accept(self):
        self.group.add_member(self.user)
        self.delete()
        return self

    def __str__(self):
        return "{} User={}".format(self.group, self.user)

    def __repr__(self):
        return "{} User={}".format(self.group, self.user)

def send_email(sender, instance, created, **kwargs):
    if created:
        deliver_email('group_invite', instance.user.profile, group=instance.group)

post_save.connect(send_email, sender=Invitation)
