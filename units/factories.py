import factory
import factory.django
import factory.fuzzy

from . import models

__all__ = ['UnitFactory']

class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Unit

    name = factory.fuzzy.FuzzyText(prefix="unit about ")
    image = factory.SubFactory('images.factories.ImageFactory')
