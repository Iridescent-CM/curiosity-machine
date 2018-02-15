import factory
import factory.django
import factory.fuzzy
from django.contrib.auth import get_user_model
from profiles.factories import *
from profiles.models import UserRole
from profiles.signals import handlers
from .models import *

__all__ = [
    'ParentProfileFactory',
    'ParentFactory',
    'ParentConnectionFactory',
]

class ParentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParentProfile

    city = 'city'

@factory.django.mute_signals(handlers.post_save)
class ParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.fuzzy.FuzzyText(prefix="parent_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user',role=UserRole.parent.value)
    parentprofile = factory.RelatedFactory(ParentProfileFactory, 'user')

class ParentConnectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParentConnection
