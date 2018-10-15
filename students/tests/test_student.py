import pytest
from django.utils.timezone import now
from profiles.factories import *
from ..factories import *
from ..models import *

def test_user_type():
    assert StudentFactory.build().extra.user_type == 'student'

@pytest.mark.django_db
def test_students_do_not_auto_approve():
    user = UserFactory()
    profile = StudentProfileFactory.build(user=user, full_access=False)
    profile.save()
    assert not user.studentprofile.full_access

@pytest.mark.django_db
def test_only_viewable_unapproved(client):
    user = StudentFactory(password="password", studentprofile__full_access=False)
    client.login(username=user.username, password="password")

    response = client.get('/student/unapproved/')
    assert response.status_code == 200

    user.studentprofile.full_access = True
    user.studentprofile.save()

    response = client.get('/student/unapproved/')
    assert response.status_code == 302
    
