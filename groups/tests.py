import pytest
import mock
from django.contrib.auth.models import User
from .models import Group, Membership, Role

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.save()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create_user(username='mentor', email='mentor@example.com', password='password')
    mentor.profile.approved = True
    mentor.profile.is_mentor = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def loggedInEducator(client):
    educator = User.objects.create_user(username='educator', email='educator@example.com', password='password')
    educator.profile.approved = True
    educator.profile.is_educator = True
    educator.profile.save()
    client.login(username='educator', password='password')
    return educator

@pytest.fixture
def group():
    return Group.objects.create(name='Group 1')

@pytest.mark.django_db
def test_students(group, student):
    Membership.objects.create(group=group, user=student, role=Role.member.value)
    assert len(group.students()) == 1
    assert len(group.educators()) == 0

@pytest.mark.django_db
def test_educators(group, mentor): #mentor for now, should change to is_educator
    Membership.objects.create(group=group, user=mentor, role=Role.owner.value)
    assert len(group.educators()) == 1
    assert len(group.students()) == 0

@pytest.mark.django_db
def test_groups(client, group, loggedInEducator):
    with mock.patch.dict('os.environ', {'ENABLE_GROUPS': '1'}):
        response = client.get('/groups/')
        assert response.status_code == 200
        assert len(response.context['groups']) == 1


@pytest.mark.django_db
def test_group(client, group, loggedInEducator):
    with mock.patch.dict('os.environ', {'ENABLE_GROUPS': '1'}):
        response = client.get('/groups/%s/' % str(group.id))
        assert response.status_code == 200
        assert response.context['group'].id == group.id