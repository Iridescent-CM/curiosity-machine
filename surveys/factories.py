import factory
import factory.django
import factory.fuzzy
from django.db.models.signals import post_save
from .models import *

__all__ = [
    'SurveyResponseFactory',
]

@factory.django.mute_signals(post_save)
class SurveyResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SurveyResponse

    user = factory.SubFactory('profiles.factories.UserFactory')
    survey_id = factory.fuzzy.FuzzyText(length=15)

    @factory.post_generation
    def status(obj, create, extracted, **kwargs):
        if extracted:
            if isinstance(extracted, str):
                extracted = ResponseStatus[extracted]
            obj.status = extracted
