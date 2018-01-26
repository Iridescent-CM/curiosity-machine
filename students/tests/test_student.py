import pytest
from django.utils.timezone import now
from profiles.factories import *
from ..factories import *
from ..models import *

def test_user_type():
    assert StudentFactory.build().extra.user_type == 'student'
    assert StudentFactory.build(studentprofile__birthday=now()).extra.user_type == 'underage student'

@pytest.mark.django_db
def test_non_coppa_students_auto_approve():
    user = UserFactory()
    profile = StudentProfileFactory.build(user=user, full_access=False)
    profile.save()
    assert user.studentprofile.full_access

@pytest.mark.django_db
def test_underage_students_do_not_auto_approve():
    user = UserFactory()
    profile = StudentProfileFactory.build(user=user, underage=True, full_access=False)
    profile.save()
    assert not user.studentprofile.full_access

@pytest.mark.django_db
def test_underage_only_viewable_unapproved(client):
    user = StudentFactory(password="password", studentprofile__full_access=False)
    client.login(username=user.username, password="password")

    response = client.get('/student/underage/')
    assert response.status_code == 200

    user.studentprofile.full_access = True
    user.studentprofile.save()

    response = client.get('/student/underage/')
    assert response.status_code == 302
    
