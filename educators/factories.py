import factory
import factory.django
import factory.fuzzy
from django.contrib.auth import get_user_model
from profiles.factories import *
from profiles.models import UserRole
from profiles.signals import handlers
from .models import *

__all__ = [
    'EducatorProfileFactory',
    'EducatorFactory',
    'ImpactSurveyFactory',
]

class EducatorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EducatorProfile

    city = 'city'

@factory.django.mute_signals(handlers.post_save)
class EducatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.fuzzy.FuzzyText(prefix="educator_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user',role=UserRole.educator.value)
    educatorprofile = factory.RelatedFactory(EducatorProfileFactory, 'user')

class ImpactSurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImpactSurvey

    user = factory.SubFactory('profiles.factories.UserFactory', educatorprofile=None)

    student_count = factory.fuzzy.FuzzyInteger(0,100)
    teacher_count = factory.fuzzy.FuzzyInteger(0,100)
    challenge_count = factory.fuzzy.FuzzyInteger(0,100)
    hours_per_challenge = factory.fuzzy.FuzzyInteger(0,100)
    in_classroom = factory.fuzzy.FuzzyChoice([True, False])
    out_of_classroom = factory.fuzzy.FuzzyChoice([True, False])
