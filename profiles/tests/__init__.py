import pytest
from django.contrib.auth.models import User
from challenges.models import Challenge, Progress

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"
PASSWORD = 'password'

@pytest.fixture
def student():
    student = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL, password=PASSWORD)
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.save()
    def fin():
        student.delete()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create(username=MENTOR_USERNAME, email=MENTOR_EMAIL, password=PASSWORD)
    mentor.profile.is_mentor = True
    mentor.profile.approved = True
    mentor.profile.save()
    def fin():
        mentor.delete()
    return mentor

@pytest.fixture
def challenge():
    thechallenge = Challenge.objects.create(name="Test Challenge")
    def fin():
        thechallenge.delete()
    return thechallenge

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def loggedInMentor(client):
    mentor = User.objects.create_user(username='mentor2', email=MENTOR_EMAIL, password=PASSWORD)
    mentor.profile.approved = True
    mentor.profile.is_mentor = True
    mentor.profile.save()
    client.login(username=mentor.username, password=PASSWORD)
    return mentor

@pytest.fixture
def loggedInStudent(client):
    student = User.objects.create_user(username='student2', email=STUDENT_EMAIL, password=PASSWORD)
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.save()
    client.login(username=student.username, password=PASSWORD)
    return student