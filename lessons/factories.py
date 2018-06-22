import factory
import factory.django

from . import models

__all__ = [
    'CommentFactory',
    'LessonFactory',
    'ProgressFactory',
]

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comment

class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Lesson

class ProgressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Progress

    lesson = factory.SubFactory('lessons.factories.LessonFactory')
    owner = factory.SubFactory('families.factories.FamilyFactory')

