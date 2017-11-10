import mock
import pytest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from memberships.factories import *
from profiles import views
from profiles.factories import *
from profiles.models import Profile, UserRole
from profiles.tests import student, mentor, progress, challenge, loggedInMentor, STUDENT_USERNAME, STUDENT_EMAIL
from students.factories import *

User = get_user_model()

@pytest.mark.django_db
def test_gets_ok(client, mentor):
    assert client.get('/join/').status_code == 200
    assert client.get('/join/some_source/').status_code == 200
    assert client.get('/join_as_mentor/').status_code == 200
    assert client.get('/join_as_mentor/source/').status_code == 200
    assert client.get('/join_as_educator/').status_code == 200
    assert client.get('/join_as_educator/source/').status_code == 200
    assert client.get('/join_as_parent/').status_code == 200
    assert client.get('/join_as_parent/source/').status_code == 200
    assert client.get('/mentors/').status_code == 200
    assert client.get('/mentors/%s/' % mentor.username).status_code == 200

@pytest.mark.django_db
def test_student_inactive_for_with_no_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_students().count() == 1

@pytest.mark.django_db
def test_student_inactive_for_with_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT) - 2)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_students().count() == 0

def test_user_type():
    assert ProfileFactory.build(user__is_superuser=True).user_type == 'admin'
    assert ProfileFactory.build(role=UserRole.mentor.value).user_type == 'mentor'
    assert ProfileFactory.build(role=UserRole.student.value).user_type == 'student'
    assert ProfileFactory.build(role=UserRole.student.value, birthday=now()).user_type == 'underage student'
    assert ProfileFactory.build(role=UserRole.educator.value).user_type == 'educator'
    assert ProfileFactory.build(role=UserRole.parent.value).user_type == 'parent'

@pytest.mark.django_db
def test_in_active_membership():
    student = StudentFactory()
    student2 = StudentFactory()
    student3 = StudentFactory()
    MembershipFactory(members=[student])
    MembershipFactory(is_active=False, members=[student3])

    assert student.profile.in_active_membership
    assert not student2.profile.in_active_membership
    assert not student3.profile.in_active_membership

@pytest.mark.django_db
def test_should_add_email():
    student = StudentFactory(email='')
    student2 = StudentFactory(email='')
    student3 = StudentFactory(email='')
    MembershipFactory(members=[student])
    MembershipFactory(is_active=False, members=[student3])

    assert student.profile.should_add_email
    assert student2.profile.should_add_email
    assert student3.profile.should_add_email

    student.email = 'email@email.com'
    student.save()
    student2.email = 'email@email.com'
    student2.save()
    student3.email = 'email@email.com'
    student3.save()

    assert not student.profile.should_add_email
    assert not student2.profile.should_add_email
    assert not student3.profile.should_add_email

@pytest.mark.django_db
def test_show_classroom_survey():
    student = StudentFactory(profile__source='')
    student2 = StudentFactory(profile__source='something')
    student3 = StudentFactory(profile__source='family_science')

    assert student.profile.show_classroom_survey
    assert student2.profile.show_classroom_survey
    assert not student3.profile.show_classroom_survey

@pytest.mark.django_db
def test_mentor_inactive_for_with_no_last_inactive_email_sent_on():
    mentor = MentorFactory()
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_mentors().count() == 1

@pytest.mark.django_db
def test_mentor_inactive_for_with_last_inactive_email_sent_on(mentor):
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR) - 2)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_mentors().count() == 0
