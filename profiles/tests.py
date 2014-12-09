import pytest
from .views import home
from django.contrib.auth.models import User
from challenges.models import Challenge, Progress
from django.utils.timezone import now
from django.conf import settings

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
    mentor.profile.is_mentor = True
    mentor.profile.save()
    client.login(username='mentor2', password='password')
    return mentor

@pytest.mark.django_db
def test_new_user_has_default_student_profile():
    user = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    assert user.profile
    assert user.profile.is_student
    assert not user.profile.is_mentor

@pytest.mark.django_db
def test_old_progress_dont_show(client, loggedInMentor, progress):
    startdate = now()
    startdate = startdate.replace(month=startdate.month - int(settings.PROGRESS_MONTH_ACTIVE_LIMIT + 1))
    progress.started = startdate
    progress.mentor = loggedInMentor
    progress.save()

    response = client.get('/home/', follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 0

@pytest.mark.django_db
def test_new_progress_will_show(client, loggedInMentor, progress):
    startdate = now()
    startdate = startdate.replace(month=startdate.month - int(settings.PROGRESS_MONTH_ACTIVE_LIMIT - 1))
    progress.started = startdate
    progress.mentor = loggedInMentor
    progress.save()

    response = client.get('/home/', follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 1
