from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

class Lesson(models.Model):
    inspiration = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    build = models.TextField(blank=True)
    further = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse("lessons:page", kwargs={
            "pk": self.id,
            "page": "inspiration"
        })

    def __str__(self):
        return "Lesson: id={}".format(self.id)
