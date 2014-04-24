import pytest
from django.contrib.auth.models import User

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"

@pytest.fixture
def student():
    return User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)

@pytest.fixture
def mentor():
    mentor = User.objects.create(username=MENTOR_USERNAME, email=MENTOR_EMAIL)
    mentor.profile.is_mentor = True
    mentor.profile.save()
    return mentor

@pytest.mark.django_db
def test_new_user_has_default_student_profile():
    user = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    assert user.profile
    assert user.profile.is_student
    assert not user.profile.is_mentor
