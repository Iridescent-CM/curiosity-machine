import factory
import factory.django
import factory.fuzzy
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.utils.timezone import now
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

    user = factory.SubFactory('students.factories.StudentFactory', profile=None)
    city = 'city'
    full_access = True

@factory.django.mute_signals(handlers.post_save)
class StudentFactory(UserFactory):
    studentprofile = factory.RelatedFactory(StudentProfileFactory, 'user')

    @factory.post_generation
    def set_role(self, create, extracted, **kwargs):
        self.extra.role = UserRole.student.value
        if create:
            self.extra.save()
