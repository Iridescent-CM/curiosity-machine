import factory
import factory.django
import factory.fuzzy

from . import models
from .signals import handlers

from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.utils.dateparse import parse_date

from django.contrib.auth import get_user_model
User = get_user_model()

# TODO: move role factories to role apps

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.UserFactory', profile=None)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        if "birthday" in kwargs:
            val = kwargs["birthday"]
            if isinstance(val, str):
                kwargs["birthday"] = parse_date(val)
        return kwargs

class UserExtraFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserExtra

    user = factory.SubFactory('profiles.factories.UserFactory', extra=None)
    approved = True

@factory.django.mute_signals(handlers.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.fuzzy.FuzzyText(prefix="user_")
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user')
    profile = factory.RelatedFactory(ProfileFactory, 'user')

class MentorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.MentorFactory', profile=None)
    city = 'city'

@factory.django.mute_signals(handlers.post_save)
class MentorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.fuzzy.FuzzyText(prefix="mentor_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user',role=models.UserRole.mentor.value)
    profile = factory.RelatedFactory(MentorProfileFactory, 'user')

class EducatorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    city = 'city'

@factory.django.mute_signals(handlers.post_save)
class EducatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.fuzzy.FuzzyText(prefix="educator_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user',role=models.UserRole.educator.value)
    profile = factory.RelatedFactory(EducatorProfileFactory, 'user')

class ImpactSurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ImpactSurvey

    user = factory.SubFactory('profiles.factories.UserFactory', profile=None)

    student_count = factory.fuzzy.FuzzyInteger(0,100)
    teacher_count = factory.fuzzy.FuzzyInteger(0,100)
    challenge_count = factory.fuzzy.FuzzyInteger(0,100)
    hours_per_challenge = factory.fuzzy.FuzzyInteger(0,100)
    in_classroom = factory.fuzzy.FuzzyChoice([True, False])
    out_of_classroom = factory.fuzzy.FuzzyChoice([True, False])