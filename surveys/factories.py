import factory
import factory.django
import factory.fuzzy
from .models import *

__all__ = [
    'SurveyResponseFactory',
]

class SurveyResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SurveyResponse

    user = factory.SubFactory('profiles.factories.UserFactory')
    survey_id = factory.fuzzy.FuzzyText(length=15)
