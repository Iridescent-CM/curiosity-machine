import factory
import factory.django
from factory import post_generation

from . import models

class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Membership

    name = factory.fuzzy.FuzzyText(prefix="membership-")

    @post_generation
    def members(obj, create, extracted, **kwargs):
        if extracted:
            for user in extracted:
                models.Member.objects.create(membership=obj, user=user)
