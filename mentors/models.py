from django.db import models
from images.models import Image
from profiles.models import BaseProfile
from videos.models import Video

class MentorProfile(BaseProfile):
    city = models.TextField(blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    title = models.TextField(blank=True)
    employer = models.TextField(blank=True)
    expertise = models.TextField(blank=True)

    about_me = models.TextField(blank=True)
    about_me_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    about_me_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    about_research = models.TextField(blank=True)
    about_research_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    about_research_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
