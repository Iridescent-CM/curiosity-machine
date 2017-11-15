import pytest
from challenges.models import Challenge, Progress
from django.contrib.auth import get_user_model
from mentors.factories import *
from profiles.models import UserRole
from students.factories import *

User = get_user_model()

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"

@pytest.fixture
def student():
    return StudentFactory(
        username=STUDENT_USERNAME,
        email=STUDENT_EMAIL,
        password='password'
    )

@pytest.fixture
def mentor():
    return MentorFactory(
        username=MENTOR_USERNAME,
        email=MENTOR_EMAIL
    )

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def loggedInMentor(client):
    mentor = MentorFactory(
        username='mentor2',
        email='mentor@example.com',
        password='password'
    )
    client.login(username='mentor2', password='password')
    return mentor
