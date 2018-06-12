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

class Progress(models.Model):
    lesson = models.ForeignKey(Lesson)
    owner = models.ForeignKey(get_user_model(), related_name='lesson_progresses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "progresses"
        unique_together = ('lesson', 'owner',)
