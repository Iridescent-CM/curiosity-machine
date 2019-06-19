import factory
import factory.django
import factory.fuzzy
from profiles.factories import *
from profiles.models import UserRole
from profiles.signals import handlers
from .models import *

__all__ = [
    'FamilyProfileFactory',
    'FamilyFactory',
    'FamilyMemberFactory',
]

class FamilyProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FamilyProfile

    user = factory.SubFactory('families.factories.FamilyFactory', familyprofile=None)
    location = factory.SubFactory('locations.factories.LocationFactory')

class FamilyMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FamilyMember

    account = factory.SubFactory('families.factories.FamilyFactory', familyprofile=None)

@factory.django.mute_signals(handlers.post_save)
class FamilyFactory(UserFactory):
    familyprofile = factory.RelatedFactory(FamilyProfileFactory, 'user')

    @factory.post_generation
    def set_role(self, create, extracted, **kwargs):
        self.extra.role = UserRole.family.value
        if create:
            self.extra.save()
