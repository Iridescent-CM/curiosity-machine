import factory
import factory.django
import factory.fuzzy
from factory import post_generation

from . import models

__all__ = [
    'MembershipFactory',
    'MemberFactory',
    'GroupFactory'
]

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

    @post_generation
    def extra_units(obj, create, extracted, **kwargs):
        if extracted:
            for unit in extracted:
                obj.extra_units.add(unit)

class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Member

    membership = factory.SubFactory('memberships.factories.MembershipFactory')

class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group

    name = factory.fuzzy.FuzzyText(prefix="group ")
    membership = factory.SubFactory('memberships.factories.MembershipFactory')

    @post_generation
    def members(obj, create, extracted, **kwargs):
        if extracted:
            for user in extracted:
                member = models.Member.objects.get(membership=obj.membership, user=user)
                models.GroupMember.objects.create(group=obj, member=member)
