import pytest
from .models import Challenge
from .views import challenges, challenge
from profiles.tests import student, mentor

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.mark.django_db
def test_challenges_response_code(challenge, student):
    request = rf.get('/challenges')
    request.user = student
    response = challenges(request)
    assert response.status_code == 200
