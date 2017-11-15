from django.db import models
from images.models import Image
from profiles.models import BaseProfile
from students.models import StudentProfile

class ParentProfile(BaseProfile):
    city = models.TextField(blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    child_profiles = models.ManyToManyField(
        StudentProfile,
        through="ParentConnection",
        through_fields=('parent_profile', 'child_profile'),
        related_name="parent_profiles",
        symmetrical=False,
        blank=True,
    )

    def is_parent_of(self, username, **kwargs):
        filters = {
            'parent_profile': self,
            'child_profile__user__username': username
        }
        for field in ['active', 'removed']:
            if field in kwargs:
                filters[field] = kwargs[field]
        return ParentConnection.objects.filter(**filters).exists()

class ParentConnection(models.Model):
    parent_profile = models.ForeignKey(ParentProfile, related_name="connections_as_parent")
    child_profile = models.ForeignKey(StudentProfile, related_name="connections_as_child")
    active = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    retries = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "ParentConnection: {} -> {}, id={}".format(
            self.parent_profile.user.username,
            self.child_profile.user.username,
            self.id
        )
