import factory
import factory.django
import factory.fuzzy

from . import models

class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Image

    source_url = "http://placehold.it/170x300"
