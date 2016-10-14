import factory
import factory.django
import factory.fuzzy

from . import models

class VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Video

    @factory.post_generation
    def thumbnails(obj, create, extracted, **kwargs):
        if extracted:
            obj.thumbnails.add(*extracted)

class EncodedVideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EncodedVideo
