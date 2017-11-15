import mock
import pytest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from memberships.factories import *
from mentors.factories import *
from profiles import views
from profiles.factories import *
from profiles.models import UserExtra, UserRole
from students.factories import *

User = get_user_model()

@pytest.mark.django_db
def test_inactive_students_not_sent():
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    StudentFactory(extra__last_active_on=enddate, extra__last_inactive_email_sent_on=None)
    assert UserExtra.inactive_students().count() == 1

@pytest.mark.django_db
def test_inactive_students_already_sent():
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT) - 2)
    StudentFactory(extra__last_active_on=enddate, extra__last_inactive_email_sent_on=last_sent_on)
    assert UserExtra.inactive_students().count() == 0

def test_user_type():
    assert UserFactory.build(is_superuser=True).extra.user_type == 'admin'

@pytest.mark.django_db
def test_in_active_membership():
    user = UserFactory()
    user2 = UserFactory()
    user3 = UserFactory()
    MembershipFactory(members=[user])
    MembershipFactory(is_active=False, members=[user3])

    assert user.extra.in_active_membership
    assert not user2.extra.in_active_membership
    assert not user3.extra.in_active_membership

@pytest.mark.django_db
def test_should_add_email():
    user = UserFactory(email='')
    user2 = UserFactory(email='')
    user3 = UserFactory(email='')
    MembershipFactory(members=[user])
    MembershipFactory(is_active=False, members=[user3])

    assert user.extra.should_add_email
    assert user2.extra.should_add_email
    assert user3.extra.should_add_email

    user.email = 'email@email.com'
    user.save()
    user2.email = 'email@email.com'
    user2.save()
    user3.email = 'email@email.com'
    user3.save()

    assert not user.extra.should_add_email
    assert not user2.extra.should_add_email
    assert not user3.extra.should_add_email

@pytest.mark.django_db
def test_show_classroom_survey():
    user = UserFactory(extra__source='')
    user2 = UserFactory(extra__source='something')
    user3 = UserFactory(extra__source='family_science')

    assert user.extra.show_classroom_survey
    assert user2.extra.show_classroom_survey
    assert not user3.extra.show_classroom_survey

@pytest.mark.django_db
def test_inactive_mentors_not_sent():
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    MentorFactory(extra__last_active_on=enddate, extra__last_inactive_email_sent_on=None)
    assert UserExtra.inactive_mentors().count() == 1

@pytest.mark.django_db
def test_inactive_mentors_already_sent():
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR) - 2)
    MentorFactory(extra__last_active_on=enddate, extra__last_inactive_email_sent_on=last_sent_on)
    assert UserExtra.inactive_mentors().count() == 0
