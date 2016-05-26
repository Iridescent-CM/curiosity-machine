import pytest
from django.contrib.auth.models import User
from challenges.models import Challenge, Progress
from profiles.models import UserRole

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"

@pytest.fixture
def student():
    student = User.objects.create_user(username=STUDENT_USERNAME, email=STUDENT_EMAIL, password='password')
    student.profile.approved = True
    student.profile.role = UserRole.student.value
    student.profile.save()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create(username=MENTOR_USERNAME, email=MENTOR_EMAIL)
    mentor.profile.role = UserRole.mentor.value
    mentor.profile.approved = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def loggedInMentor(client):
    mentor = User.objects.create_user(username='mentor2', email='mentor@example.com', password='password')
    mentor.profile.approved = True
    mentor.profile.role = UserRole.mentor.value
    mentor.profile.save()
    client.login(username='mentor2', password='password')
    return mentor
