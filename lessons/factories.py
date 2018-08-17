import factory
import factory.django
import factory.fuzzy

from . import models

__all__ = [
    'CommentFactory',
    'LessonFactory',
    'ProgressFactory',
    'QuizFactory',
    'QuizResultFactory',
]

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comment

class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Lesson

    quiz = factory.SubFactory('lessons.factories.QuizFactory')

class ProgressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Progress

    lesson = factory.SubFactory('lessons.factories.LessonFactory')
    owner = factory.SubFactory('families.factories.FamilyFactory')

class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Quiz

    question_1 = factory.fuzzy.FuzzyText(prefix="Quiz question ")
    answer_1_1 = factory.fuzzy.FuzzyText(prefix="Answer 1 ")
    answer_1_2 = factory.fuzzy.FuzzyText(prefix="Answer 2 ")
    answer_1_3 = factory.fuzzy.FuzzyText(prefix="Answer 3 ")
    correct_answer_1 = 1
    explanation_1 = factory.fuzzy.FuzzyText(prefix="Explanation text ")

class QuizResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.QuizResult

    answer_1 = 1

