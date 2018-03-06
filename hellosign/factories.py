import factory
import factory.django
import factory.fuzzy
from django.db.models.signals import post_save
from .models import *

__all__ = [
    'SignatureFactory',
]

@factory.django.mute_signals(post_save)
class SignatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Signature

    user = factory.SubFactory('profiles.factories.UserFactory')
    template_id = factory.fuzzy.FuzzyText(length=15)
