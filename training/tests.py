import pytest
from .models import Module
from .views import module as module_view
from profiles.tests import student, mentor

@pytest.fixture
def module():
    return Module.objects.create(id=1)

@pytest.mark.django_db
def test_training_response_code(rf, student, mentor, module):
    request = rf.get('/training/1/')
    request.user = student
    response = module_view(request, module.id)
    assert response.status_code == 403

    request = rf.get('/training/1/')
    request.user = mentor
    response = module_view(request, module.id)
    assert response.status_code == 200

    mentor.profile.approved = False
    request = rf.get('/training/1/')
    request.user = mentor
    response = module_view(request, module.id)
    assert response.status_code == 200
