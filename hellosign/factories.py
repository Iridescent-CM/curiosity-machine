import factory
import factory.django
import factory.fuzzy
from .models import *

__all__ = [
    'SignatureFactory',
]

class SignatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Signature

    user = factory.SubFactory('profiles.factories.UserFactory')
    template_id = factory.fuzzy.FuzzyText(length=15)
