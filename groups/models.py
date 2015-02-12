from django.db import models
from profiles.models import Profile
from enum import Enum
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify #use slugify for now

class Role(Enum):
    educator = 0
    student = 1

class Group(models.Model):
    name = models.CharField('name', max_length=80, unique=True, null=True, blank=False)
    code = models.CharField('code', max_length=20, unique=True, null=True, blank=False)
    members = models.ManyToManyField(Profile, through='Membership', through_fields=('group', 'profile'), related_name="groups")

    def educators(self):
        return self.with_role(Role.educator.value)

    def students(self):
        return self.with_role(Role.student.value)

    def with_role(self,role=Role.educator.value):
       return map(lambda x:x.profile, Membership.objects.select_related('profile').filter(group=self,role=role).all()) 

    def __str__(self):
        return "Group={}".format(self.name)

    def __repr__(self):
        return "Group={}".format(self.name)


def create_slug(sender, instance, **kwargs):
    #probably going to replace how to generate the code
    instance.code = slugify(instance.name)[:20]

pre_save.connect(create_slug, sender=Group)

class Membership(models.Model):
    group = models.ForeignKey(Group)
    profile = models.ForeignKey(Profile)
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in Role], default=Role.educator.value)

    def __str__(self):
        return "Group={} Profile={}".format(self.group, self.profile)

    def __repr__(self):
        return "Group={} Profile={}".format(self.group, self.profile)
