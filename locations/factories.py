import factory
import factory.django
import factory.fuzzy
from .models import *

__all__ = [
    'LocationFactory',
]

class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    state = factory.fuzzy.FuzzyChoice((pair[0] for pair in US_STATE_CHOICES))
    city = "Springfield"
