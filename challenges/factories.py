import factory
import factory.django
import factory.fuzzy
from factory import post_generation

from . import models

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
