import factory
import factory.django
import factory.fuzzy
from factory import post_generation
import random

from . import models

from cmcomments.factories import CommentFactory

__all__ = [
    'QuestionFactory',
    'ChallengeFactory',
    'ProgressFactory',
    'ExampleFactory',
    'FilterFactory',
    'ThemeFactory',
    'ResourceFactory',
    'ResourceFileFactory',
]

class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Question

    text = factory.fuzzy.FuzzyText(prefix="Question: ", suffix="?")

class ChallengeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Challenge

    name = factory.fuzzy.FuzzyText(prefix="challenge-") 
    description = "description"
    how_to_make_it = "how to make it"
    learn_more = "learn more"
    materials_list = "<ul><li>material 1</li><li>material 2</li><li>material 3</li></ul>"
    plan_call_to_action = "call to action"
    build_call_to_action = "call to action"
    plan_subheader = "subheader"
    build_subheader = "subheader"
    reflect_subheader = "subheader"
    image = factory.SubFactory('images.factories.ImageFactory')

    @factory.post_generation
    def themes(obj, create, extracted, **kwargs):
        if extracted:
            obj.themes.add(*extracted)

    @factory.post_generation
    def reflect_questions(obj, create, extracted, **kwargs):
        if extracted:
            obj.reflect_questions.add(*extracted)


class ProgressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Progress

    challenge = factory.SubFactory('challenges.factories.ChallengeFactory')
    student = factory.SubFactory('profiles.factories.StudentFactory')

    @factory.post_generation
    def comment(obj, create, extracted, **kwargs):
        if extracted:
            if not create:
                raise NotImplementedError('only CREATE strategy is handled so far, not BUILD')

            obj.comments.create(user=obj.student, text="First post!", stage=1)
            if isinstance(extracted, int) and extracted > 1:
                for idx in range(1, extracted):
                    if obj.mentor:
                        user = random.choice([obj.student, obj.mentor])
                    else:
                        user = obj.student
                    obj.comments.add(CommentFactory(challenge_progress=obj, user=user))

    @factory.post_generation
    def completed(obj, create, extracted, **kwargs):
        if extracted:
            if not create:
                raise NotImplementedError('only CREATE strategy is handled so far, not BUILD')

            obj.comments.create(user=obj.student, text="Reflection", stage=4, question_text="Reflect question text")

class ExampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Example

    progress = factory.SubFactory('challenges.factories.ProgressFactory')
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

class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Resource

class ResourceFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ResourceFile
