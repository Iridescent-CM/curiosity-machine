import pytest
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
def group():
    return Group.objects.create(name='Group 1')

@pytest.mark.django_db
def test_students(group, student):
    Membership.objects.create(group=group, user=student, role=Role.student.value)
    assert len(group.students()) == 1
    assert len(group.educators()) == 0

@pytest.mark.django_db
def test_educators(group, mentor): #mentor for now, should change to is_educator
    Membership.objects.create(group=group, user=mentor, role=Role.educator.value)
    assert len(group.educators()) == 1
    assert len(group.students()) == 0

@pytest.mark.django_db
def test_code_slug():
    group = Group.objects.create(name='Group 1')
    assert group.code == 'group-1'

@pytest.mark.django_db
def test_groups(client, group):
    response = client.get('/groups/')
    assert response.status_code == 200
    assert len(response.context['groups']) == 1


@pytest.mark.django_db
def test_group(client, group):
    response = client.get('/groups/%s/' % str(group.id))
    assert response.status_code == 200
    assert response.context['group'].id == group.id