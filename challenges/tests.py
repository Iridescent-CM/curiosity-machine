import pytest
from .models import Challenge, Progress
from .views import challenges, challenge_progress_approve
from .views import challenge as challenge_view # avoid conflict with appropriately-named fixture
from profiles.tests import student, mentor
from django.contrib.auth.models import AnonymousUser
from .templatetags.user_has_started_challenge import user_has_started_challenge

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.fixture
def challenge2():
    return Challenge.objects.create(name="Test Challenge 2")

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.mark.django_db
def test_challenges_response_code(rf, challenge, student):
    request = rf.get('/challenges/')
    response = challenges(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenge_response_code(rf, challenge, student):
    request = rf.get('/challenges/1/')
    request.user = AnonymousUser()
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200

    request = rf.get('/challenges/1/')
    request.user = student
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_has_started_challenge(progress, challenge2):
    student = progress.student
    challenge = progress.challenge
    assert user_has_started_challenge(student, challenge)
    assert not user_has_started_challenge(student, challenge2)

@pytest.mark.django_db
def test_mentor_can_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve')
    request.user = progress.mentor
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert Progress.objects.get(id=progress.id).approved

    request = rf.delete('/challenges/1/approve')
    request.user = progress.mentor
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert not Progress.objects.get(id=progress.id).approved

@pytest.mark.django_db
def test_student_cannot_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve')
    request.user = progress.student
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 403
    assert not Progress.objects.get(id=progress.id).approved
