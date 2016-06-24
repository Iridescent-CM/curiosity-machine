import factory
import factory.django

from . import models

class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Membership
