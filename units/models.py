import os

from django.db import models
from django.core.urlresolvers import reverse
from images.models import Image
from challenges.models import Challenge
from s3direct.fields import S3DirectField


class Unit(models.Model):
    name = models.TextField(blank=False, null=False, help_text="name of the unit")
    description = models.TextField(blank=True, null=True, help_text="blurb for the unit")
    overview = models.TextField(blank=True, null=True, help_text="overview for the unit")
    challenges = models.ManyToManyField(Challenge, through='UnitChallenge', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="image")
    standards_alignment_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="unit")
    draft = models.BooleanField(default=True, null=False, help_text="Drafts are not shown on the main units page")

    def get_absolute_url(self):
        return reverse('units:unit', kwargs={
            'unit_id': self.id
        })

    def __str__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)

    def __repr__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)

class UnitChallenge(models.Model):
    unit = models.ForeignKey(Unit)
    challenge = models.ForeignKey(Challenge)
    display_order = models.PositiveIntegerField()

class Resource(models.Model):
    units = models.ManyToManyField(Unit, related_name="resources", blank=True)
    link_text = models.CharField(max_length=128)
    file = S3DirectField(dest='unit-resources', blank=True, null=True, help_text="Uploads will overwrite files of the same name")

    def __str__(self):
        return "Resource: id={}, text={}, file={}".format(self.id, self.link_text, os.path.basename(self.file))