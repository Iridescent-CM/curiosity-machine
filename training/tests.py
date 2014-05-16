from .models import Module
from .views import module
from profile.tests import student, mentor

@pytest.mark.django_db
def test_training_response_code(student, mentor, module):
    request = rf.get('/training/1/')
    request.user = student
    response = module(request, module.id)
    assert response.status_code == 403

    request = rf.get('/training/1/')
    request.user = mentor
    response = module(request, module.id)
    assert response.status_code == 200

    mentor.profile.approved = False
    request = rf.get('/training/1/')
    request.user = mentor
    response = module(request, module.id)
    assert response.status_code == 200
