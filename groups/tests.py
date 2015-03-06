import pytest
import mock
from mock import patch
from django.contrib.auth.models import User
from .models import Group, Membership, Role, INVITATIONS_NS
from django_simple_redis import redis

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
def test_group_add_member(group, student):
    assert len(group.members()) == 0
    group.add_member(student)
    assert len(group.members()) == 1

@pytest.mark.django_db
@pytest.mark.redis
def test_group_invite_member(group, student):
    redis.flushall()
    keys = redis.keys(INVITATIONS_NS.format(group_id=str(group.id), token="*"))
    assert len(keys) == 0
    group.invite_member(student)
    keys = redis.keys(INVITATIONS_NS.format(group_id=str(group.id), token="*"))
    assert len(keys) == 1

@pytest.mark.django_db
@pytest.mark.redis
def test_group_accept_invitation(group, student):
    redis.flushall()
    group.invite_member(student)
    keys = redis.keys(INVITATIONS_NS.format(group_id=str(group.id), token="*"))
    assert len(keys) == 1
    token = keys[0].decode("utf-8").split(":")[-1]
    group.accept_invitation(token)
    assert len(group.members()) == 1

@pytest.mark.django_db
def test_group_delete_member(group, student):
    group.add_member(student)
    assert len(group.members()) == 1
    group.delete_member(student)
    assert len(group.members()) == 0

    
@pytest.mark.django_db
def test_group_add_owner(group, mentor):
    assert len(group.owners()) == 0
    group.add_owner(mentor)
    assert len(group.owners()) == 1

@pytest.mark.django_db
def test_students(group, student):
    Membership.objects.create(group=group, user=student, role=Role.member.value)
    assert len(group.members()) == 1
    assert len(group.owners()) == 0

@pytest.mark.django_db
def test_educators(group, mentor): #mentor for now, should change to is_educator
    Membership.objects.create(group=group, user=mentor, role=Role.owner.value)
    assert len(group.owners()) == 1
    assert len(group.members()) == 0

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

