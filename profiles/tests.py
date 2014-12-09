import pytest
from django.contrib.auth.models import User
from profiles.models import Profile
from django.utils.timezone import now
from datetime import date, timedelta

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"

@pytest.fixture
def student():
    student = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    student.profile.approved = True
    student.profile.save()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create(username=MENTOR_USERNAME, email=MENTOR_EMAIL)
    mentor.profile.is_mentor = True
    mentor.profile.approved = True
    mentor.profile.save()
    return mentor

@pytest.mark.django_db
def test_new_user_has_default_student_profile():
    user = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    assert user.profile
    assert user.profile.is_student
    assert not user.profile.is_mentor

@pytest.mark.django_db
def test_student_inactive_for_with_no_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=15)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_students().count() == 1

@pytest.mark.django_db
def test_student_inactive_for_with_gt_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=15)
    last_sent_on = startdate - timedelta(days=14)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_students().count() == 0

@pytest.mark.django_db
def test_student_inactive_for_with_lt_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=15)
    last_sent_on = startdate - timedelta(days=16)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_students().count() == 0


@pytest.mark.django_db
def test_mentor_inactive_for_with_no_last_inactive_email_sent_on(mentor):
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=8)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_mentors().count() == 1

@pytest.mark.django_db
def test_mentor_inactive_for_with_last_inactive_email_sent_on(mentor):
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=8)
    last_sent_on = startdate - timedelta(days=7)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_mentors().count() == 0
