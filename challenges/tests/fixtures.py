import pytest
from django.contrib.auth import get_user_model
from cmcomments.models import Comment
from challenges.models import Challenge, Progress, Theme, Favorite, Filter
from profiles.models import UserRole
from profiles.factories import *

User = get_user_model()

@pytest.fixture
def loggedInStudent(client):
    student = StudentFactory(
        username='loggedinstudent',
        email='loggedinstudent@example.com',
        password='password'
    )
    client.login(username='loggedinstudent', password='password')
    return student

@pytest.fixture
def loggedInStaff(client):
    staff = User.objects.create_superuser(username='staff', email='staff@example.com', password='password')
    client.login(username='staff', password='password')
    return staff

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.fixture
def theme():
    return Theme.objects.create(name="MyTheme")

@pytest.fixture
def challenge():
    return Challenge.objects.create(
        name="Test Challenge",
        draft=False,
        reflect_subheader='test reflect_subheader',
        build_subheader='test build_subheader'
    )

@pytest.fixture
def filter():
    return Filter.objects.create(name="My Filter")

@pytest.fixture
def challenge2():
    return Challenge.objects.create(name="Test Challenge 2", draft=False)

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def unclaimed_progress(student, challenge):
    return Progress.objects.create(student=student, challenge=challenge)
