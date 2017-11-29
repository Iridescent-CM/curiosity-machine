import factory
import factory.django
import factory.fuzzy
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from factory import post_generation

from . import models

__all__ = [
    'MembershipFactory',
    'MemberFactory',
    'GroupFactory',
    'CSVRowDataFactory',
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

class CSVRowDataFactory(factory.Factory):
    class Meta:
        model = dict

    first_name = factory.fuzzy.FuzzyText(prefix="fn_")
    last_name = factory.fuzzy.FuzzyText(prefix="ln_")
    password = factory.fuzzy.FuzzyText(length=6)
    username = factory.fuzzy.FuzzyText()
    email = factory.fuzzy.FuzzyText(suffix="@mailinator.com")
    birthday = factory.fuzzy.FuzzyDate(
        start_date=now() - relativedelta(years=30),
        end_date=now() - relativedelta(years=14)
    )

    class Params:
        underage = factory.Trait(
            birthday=factory.fuzzy.FuzzyDate(
                start_date=now() - relativedelta(years=12),
                end_date=now() - relativedelta(years=5)
            )
        )
