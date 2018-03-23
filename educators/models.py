from django.conf import settings
from django.db import models
from images.models import Image
from locations.models import Location
from profiles.models import BaseProfile
from django.utils.functional import cached_property
from surveys import get_survey

class EducatorProfile(BaseProfile):
    city = models.TextField(blank=True) # deprecated, use location
    location = models.ForeignKey(Location, null=True, blank=False, on_delete=models.PROTECT)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.CharField(max_length=50, null=True, blank=True)
	  title_i = models.BooleanField(default=False, null=False)

    @cached_property
    def full_coach_access(self):
        presurvey = get_survey(settings.AICHALLENGE_COACH_PRE_SURVEY_ID)
        if self.is_coach and presurvey.active:
            response = presurvey.response(self.user)
            return response.completed
        return False

    @cached_property
    def is_coach(self):
        return self.user.membership_set.filter(is_active=True, id=settings.AICHALLENGE_COACH_MEMBERSHIP_ID).exists()

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
