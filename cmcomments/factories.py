import factory
import factory.django
import factory.fuzzy

from . import models

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comment
