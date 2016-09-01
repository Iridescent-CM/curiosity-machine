import factory
import factory.django
import factory.fuzzy

from . import models

class ChallengeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Challenge

    name = factory.fuzzy.FuzzyText(prefix="challenge-")

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
