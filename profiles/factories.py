import factory
import factory.django
import factory.fuzzy
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.dateparse import parse_date
from .models import *
from .signals import handlers

__all__ = [
    'UserExtraFactory',
    'UserFactory',
]

@factory.django.mute_signals(post_save)
class UserExtraFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserExtra

    user = factory.SubFactory('profiles.factories.UserFactory', extra=None)

class EmailAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    email = factory.fuzzy.FuzzyText(suffix="@mailinator.com")
    verified = False
    primary = True

@factory.django.mute_signals(handlers.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.fuzzy.FuzzyText(prefix="user_")
    password = factory.PostGenerationMethodCall('set_password', '123123')
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)

    extra = factory.RelatedFactory(UserExtraFactory, 'user')

    @factory.post_generation
    def sync_email(self, create, extracted, **kwargs):
        if not create:
            return
        EmailAddressFactory(user=self, email=self.email)