from django.db import models
from challenges.models import Challenge
from profiles.models import UserRole
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Membership(models.Model):
    name = models.CharField(unique=True, max_length=255, null=False, blank=False)
    expiration = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    challenges = models.ManyToManyField(Challenge, blank=True)
    members = models.ManyToManyField(User, through='Member', through_fields=('membership', 'user'), blank=True)

    def limit_for(self, role):
        obj = self.memberlimit_set.filter(role=role).first()
        if obj:
            return obj.limit
        return None

    def __str__(self):
        return self.name

class Member(models.Model):
    membership = models.ForeignKey(Membership)
    user = models.ForeignKey(User)

    def clean(self):
        role = self.user.profile.role
        limit = self.membership.limit_for(role)
        if limit != None:
            count = (self.membership.member_set
                .exclude(id=self.id)
                .filter(user__profile__role=role)).count()
            if count >= limit:
                raise ValidationError("%s membership in %s limited to %d" % (UserRole(role).name, self.membership, limit))

class MemberLimit(models.Model):
    class Meta:
        unique_together = ("role", "membership")
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in UserRole], default=UserRole.none.value)
    limit = models.PositiveIntegerField(null=False, blank=True, default=0)
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)

from django.db.models.signals import pre_save
from django.dispatch import receiver
@receiver(pre_save, sender=Member)
def clean_first(sender, instance, **kwargs):
    instance.full_clean()
