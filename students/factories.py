import factory
import factory.django
import factory.fuzzy
from django.contrib.auth import get_user_model
from profiles.factories import *
from profiles.models import UserRole
from profiles.signals import handlers
from .models import *

__all__ = [
    'StudentProfileFactory',
    'StudentFactory',
]

class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory('profiles.factories.StudentFactory', profile=None)
    city = 'city'
    birthday = now() - relativedelta(years=14)

    class Params:
        underage = factory.Trait(
            birthday=now() - relativedelta(years=12)
        )

@factory.django.mute_signals(handlers.post_save)
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.fuzzy.FuzzyText(prefix="student_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    extra = factory.RelatedFactory(UserExtraFactory, 'user',role=UserRole.student.value)
    profile = factory.RelatedFactory(StudentProfileFactory, 'user')
