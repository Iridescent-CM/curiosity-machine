import factory
import factory.django
import factory.fuzzy
from factory import post_generation

from . import models

class ChallengeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Challenge

class ProgressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Progress

    challenge = factory.SubFactory('challenges.factories.ChallengeFactory')
    student = factory.SubFactory('profiles.factories.StudentFactory')

    @factory.post_generation
    def comment(obj, create, extracted, **kwargs):
        if extracted:
            obj.comments.create(user=obj.student, text="First post!", stage=1)

    @factory.post_generation
    def completed(obj, create, extracted, **kwargs):
        if extracted:
            obj.comments.create(user=obj.student, text="Reflection", stage=4, question_text="Reflect question text")

class ExampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Example

    challenge = factory.SubFactory('challenges.factories.ChallengeFactory')
    progress = factory.SubFactory('challenges.factories.ProgressFactory', challenge=factory.SelfAttribute('..challenge'))
    image = factory.SubFactory('images.factories.ImageFactory')

class FilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Filter

    name = factory.fuzzy.FuzzyText(prefix="filter-")
    visible = True

    @post_generation
    def challenges(obj, create, extracted, **kwargs):
        if extracted:
            for challenge in extracted:
                obj.challenges.add(challenge)

class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Theme

    name = factory.fuzzy.FuzzyText(prefix="theme-")

    @post_generation
    def challenges(obj, create, extracted, **kwargs):
        if extracted:
            for challenge in extracted:
                challenge.themes.add(obj)
