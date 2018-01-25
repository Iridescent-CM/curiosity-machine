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
    user = UserFactory(extra__approved=False)
    profile = StudentProfileFactory.build(user=user)
    profile.save()
    assert user.extra.approved

@pytest.mark.django_db
def test_underage_students_do_not_auto_approve():
    user = UserFactory(extra__approved=False)
    profile = StudentProfileFactory.build(user=user, underage=True)
    profile.save()
    assert not user.extra.approved

@pytest.mark.django_db
def test_underage_only_viewable_unapproved(client):
    user = StudentFactory(password="password", extra__approved=False)
    client.login(username=user.username, password="password")

    response = client.get('/student/underage/')
    assert response.status_code == 200

    user.extra.approved = True
    user.extra.save()

    response = client.get('/student/underage/')
    assert response.status_code == 302
    
