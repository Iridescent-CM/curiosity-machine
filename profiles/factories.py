import factory
import factory.django
import factory.fuzzy

from . import models

class MentorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory('profiles.factories.MentorFactory', profile=None)
    city = 'city'
    is_mentor = True
    approved = True

@factory.django.mute_signals(models.post_save)
class MentorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.fuzzy.FuzzyText(prefix="mentor_")
    email = factory.LazyAttribute(lambda obj: '%s@mailinator.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', '123123')

    profile = factory.RelatedFactory(MentorProfileFactory, 'user')