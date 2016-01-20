import factory
import factory.django
import factory.fuzzy

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

class ExampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Example

    progress = factory.SubFactory('challenges.factories.ProgressFactory')
    image = factory.SubFactory('images.factories.ImageFactory')
