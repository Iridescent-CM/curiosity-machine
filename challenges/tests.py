import pytest
from .models import Challenge
from .views import challenges
from .views import challenge as challenge_view # avoid conflict with appropriately-named fixture
from profiles.tests import student, mentor
from django.contrib.auth.models import AnonymousUser

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.mark.django_db
def test_challenges_response_code(rf, challenge, student):
    request = rf.get('/challenges')
    response = challenges(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenge_response_code(rf, challenge, student):
    request = rf.get('/challenges/1/')
    request.user = AnonymousUser()
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200

    request = rf.get('/challenges')
    request.user = student
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200
