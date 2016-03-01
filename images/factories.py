import factory
import factory.django
import factory.fuzzy

from . import models

class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Image
        exclude = ('_width', '_height')

    _width = factory.fuzzy.FuzzyInteger(100, 800)
    _height = factory.fuzzy.FuzzyInteger(100, 800)
    source_url = factory.LazyAttribute(lambda o: "http://placehold.it/%dx%d" % (o._width, o._height))
