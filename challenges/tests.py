import pytest
from .models import Challenge, Progress
from .views import challenges, challenge_progress_approve, unclaimed_progresses, claim_progress
from .views import challenge as challenge_view # avoid conflict with appropriately-named fixture
from profiles.tests import student, mentor
from django.contrib.auth.models import AnonymousUser
from .templatetags.user_has_started_challenge import user_has_started_challenge
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.fixture
def challenge2():
    return Challenge.objects.create(name="Test Challenge 2")

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def unclaimed_progress(student, challenge):
    return Progress.objects.create(student=student, challenge=challenge)

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
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert Progress.objects.get(id=progress.id).approved

    request = rf.delete('/challenges/1/approve')
    request.user = progress.mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert not Progress.objects.get(id=progress.id).approved

@pytest.mark.django_db
def test_student_cannot_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve')
    request.user = progress.student
    with pytest.raises(PermissionDenied):
        response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert not Progress.objects.get(id=progress.id).approved

@pytest.mark.django_db
def test_unclaimed_progresses_response_code(rf, mentor, unclaimed_progress):
    request = rf.get('/challenges/unclaimed/')
    request.user = mentor
    response = unclaimed_progresses(request)
    assert response.status_code == 200

    request = rf.get('/challenges/unclaimed/')
    request.user = unclaimed_progress.student
    with pytest.raises(PermissionDenied):
        response = unclaimed_progresses(request)

@pytest.mark.django_db
def test_claim_progress(rf, mentor, unclaimed_progress):
    assert not unclaimed_progress.mentor

    request = rf.post('/challenges/unclaimed/1')
    request.user = mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = claim_progress(request, unclaimed_progress.id)
    assert response.status_code == 302
    assert Progress.objects.get(id=unclaimed_progress.id).mentor == mentor

@pytest.mark.django_db
def test_student_cannot_claim_progress(rf, unclaimed_progress):
    assert not unclaimed_progress.mentor

    request = rf.post('/challenges/unclaimed/1')
    request.user = unclaimed_progress.student
    with pytest.raises(PermissionDenied):
        response = claim_progress(request, unclaimed_progress.id)
    assert not Progress.objects.get(id=unclaimed_progress.id).mentor
