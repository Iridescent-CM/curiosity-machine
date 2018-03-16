from django.conf import settings
from django.db import models
from images.models import Image
from locations.models import Location
from profiles.models import BaseProfile

class EducatorProfile(BaseProfile):
    city = models.TextField(blank=True) # deprecated, use location
    location = models.ForeignKey(Location, null=True, blank=False, on_delete=models.PROTECT)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.CharField(max_length=50, null=True, blank=True)
    title_i = models.BooleanField(default=False, null=False)

class ImpactSurvey(models.Model):
    student_count = models.PositiveIntegerField(default=0, blank=True)
    teacher_count = models.PositiveIntegerField(default=0, blank=True)
    challenge_count = models.PositiveIntegerField(default=0, blank=True)
    in_classroom = models.BooleanField(default=False)
    out_of_classroom = models.BooleanField(default=False)
    hours_per_challenge = models.PositiveIntegerField(default=0, blank=True)
    comment = models.TextField(blank=True, default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "ImpactSurvey: id={}, user_id={}".format(self.id, self.user_id)
