import factory
import factory.django
import factory.fuzzy

from . import models
from .signals import handlers

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.UserFactory', profile=None)

@factory.django.mute_signals(handlers.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    profile = factory.RelatedFactory(ProfileFactory, 'user')

class MentorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.MentorFactory', profile=None)
    city = 'city'
    role = models.UserRole.mentor.value
    approved = True

@factory.django.mute_signals(handlers.post_save)
class MentorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.fuzzy.FuzzyText(prefix="mentor_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    profile = factory.RelatedFactory(MentorProfileFactory, 'user')

class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.StudentFactory', profile=None)
    city = 'city'
    role = models.UserRole.student.value
    approved = True

@factory.django.mute_signals(handlers.post_save)
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.fuzzy.FuzzyText(prefix="student_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    profile = factory.RelatedFactory(StudentProfileFactory, 'user')