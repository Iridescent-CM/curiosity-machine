import factory
import factory.django

from . import models

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Task
