import factory
import factory.django
import factory.fuzzy
from factory import post_generation

from . import models

class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Membership

    name = factory.fuzzy.FuzzyText(prefix="name ")
    display_name = factory.fuzzy.FuzzyText(prefix="display name ")

    @post_generation
    def members(obj, create, extracted, **kwargs):
        if extracted:
            for user in extracted:
                models.Member.objects.create(membership=obj, user=user)

    @post_generation
    def challenges(obj, create, extracted, **kwargs):
        if extracted:
            for challenge in extracted:
                obj.challenges.add(challenge) 
