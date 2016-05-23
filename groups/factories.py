import factory
import factory.django
import factory.fuzzy

from . import models

class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group

    name = factory.fuzzy.FuzzyText(prefix="group_")

    @factory.post_generation
    def members(obj, create, extracted, **kwargs):
        for member in extracted:
            obj.add_member(member)

    @factory.post_generation
    def owners(obj, create, extracted, **kwargs):
        for owner in extracted:
            obj.add_owner(owner)
