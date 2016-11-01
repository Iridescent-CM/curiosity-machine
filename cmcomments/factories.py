import factory
import factory.django
import factory.fuzzy

from . import models
from challenges.models import Stage
from django.conf import settings

__all__ = [
    "CommentFactory",
    "ReflectionCommentFactory",
]

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comment

    text = factory.fuzzy.FuzzyText(prefix='comment text ')
    stage = factory.fuzzy.FuzzyChoice([
        #Stage.inspiration.value, # this is not a stage that gets commented in
        Stage.plan.value,
        Stage.build.value,
        Stage.test.value
        # no Stage.reflect.value by default because of its special semantics for completedness
    ])
    question_text = factory.LazyAttribute(lambda o: "This is the question text." if Stage(int(o.stage)) == Stage.reflect else "")

    # NB: this generates a non-reflect comment then modifies it; so signals might not work
    @factory.post_generation
    def reflection(obj, create, extracted, **kwargs):
        if extracted:
            obj.stage = Stage.reflect.value
            obj.question_text = "This is the question text."

class ReflectionCommentFactory(CommentFactory):
    stage = Stage.reflect.value
    question_text = factory.fuzzy.FuzzyText(prefix='question text ')
