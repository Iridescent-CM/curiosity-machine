from django.db import models
from images.models import Image
from challenges.models import Challenge
from files.models import File

class Unit(models.Model):
    name = models.TextField(blank=False, null=False, help_text="name of the unit")
    description = models.TextField(blank=True, null=True, help_text="blurb for the unit")
    overview = models.TextField(blank=True, null=True, help_text="overview for the unit")
    challenges = models.ManyToManyField(Challenge, related_name='units')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    standards_alignment_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="unit")

    def __str__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)

    def __repr__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)

class Resource(models.Model):
    name = models.TextField(blank=False, null=False, help_text="name of the resource")
    file = models.ForeignKey(File, null=True, blank=True, on_delete=models.SET_NULL)
    unit = models.ForeignKey(Unit, blank=False, null=False, related_name="resources")