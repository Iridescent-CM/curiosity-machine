import pytest
import mock
from mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from .models import Group, Membership, Role, Invitation
from . import views
from . import decorators
from django.core.urlresolvers import reverse
from django.conf import settings
from profiles.models import Profile, UserRole
from django.core.exceptions import PermissionDenied

User = get_user_model()

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.role = UserRole.student.value
    student.profile.save()
    return student

@pytest.fixture
def educator():
    educator = User.objects.create_user(username='educator', email='educator@example.com', password='password')
    educator.profile.approved = True
    educator.profile.role = UserRole.educator.value
    educator.profile.save()
    return educator

@pytest.fixture
def mentor():
    mentor = User.objects.create_user(username='mentor', email='mentor@example.com', password='password')
    mentor.profile.approved = True
    mentor.profile.role = UserRole.mentor.value
    mentor.profile.save()
    return mentor

@pytest.fixture
def loggedInEducator(client, educator):
    client.login(username=educator.username, password='password')
    return educator

@pytest.fixture
def loggedInStudent(client, student):
    client.login(username=student.username, password='password')
    return student

@pytest.fixture
def group():
    return Group.objects.create(name='Group 1')

@pytest.mark.django_db
def test_group_add_member(group, student):
    assert len(group.members()) == 0
    group.add_member(student)
    assert len(group.members()) == 1

@pytest.mark.django_db
def test_group_invite_member(group, student):
    group.invite_member(student)
    assert Invitation.objects.count() == 1

@pytest.mark.django_db
def test_group_invite_member_skips_existing_member(group, student):
    group.invite_member(student)
    assert Invitation.objects.count() == 1
    Invitation.objects.first().accept()
    group.invite_member(student)
    assert Invitation.objects.count() == 0

@pytest.mark.django_db
def test_group_accept_invitation(group, student):
    group.invite_member(student)
    invitation = Invitation.objects.first()
    invitation.accept()
    assert len(group.members()) == 1
    assert Invitation.objects.count() == 0

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
def test_educators(group, mentor):
    Membership.objects.create(group=group, user=mentor, role=Role.owner.value)
    assert len(group.owners()) == 1
    assert len(group.members()) == 0

@pytest.mark.django_db
def test_group(client, group, loggedInEducator):
    group.add_owner(loggedInEducator)
    response = client.get('/groups/%s/' % str(group.id))
    assert response.status_code == 200
    assert response.context['group'].id == group.id

@pytest.mark.django_db
def test_group_permission_denied_to_non_owners(client, loggedInEducator, group):
    response = client.get('/groups/%s/' % group.id)
    assert response.status_code == 403

@pytest.mark.django_db
def test_join_group(client, group, loggedInStudent):
    response = client.post(reverse('groups:join_group'), {'code': group.code}, HTTP_REFERER='/')
    assert len(group.members()) == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_leave_group(client, group, loggedInStudent):
    group.add_member(loggedInStudent)
    response = client.post(reverse('groups:leave', kwargs={'group_id': group.id}))
    assert len(group.members()) == 0
    assert response.status_code == 302

@pytest.mark.django_db
def test_invite_to_group(client, group, student, loggedInEducator):
    group.add_owner(loggedInEducator)
    response = client.post(
        reverse('groups:invite_to_group', kwargs={'group_id': group.id}),
        {'recipients': student.username}
    )
    assert Invitation.objects.filter(user=student, group=group).exists()
    assert response.status_code == 302

@pytest.mark.django_db
def test_resend_invite_to_group(client, group, student, loggedInEducator):
    qs = '?resend=1'
    group.add_owner(loggedInEducator)
    response = client.post(
        reverse('groups:invite_to_group', kwargs={'group_id': group.id}) + qs,
        {'recipients': student.username},
        follow=True
    )
    assert Invitation.objects.filter(user=student, group=group).exists()
    messages = list(response.context['messages'])
    assert len(messages) == 1
    assert "Resent" in str(messages[0])

@pytest.mark.django_db
def test_invite_multiple_to_group(client, group, student, loggedInEducator):
    group.add_owner(loggedInEducator)
    otherstudent = User.objects.create_user(username='otherstudent', email='student@example.com', password='password')
    otherstudent.profile.approved = True
    otherstudent.profile.role = UserRole.student.value
    otherstudent.profile.save()
    response = client.post(
        reverse('groups:invite_to_group', kwargs={'group_id': group.id}),
        {'recipients': ", ".join([student.username, otherstudent.username])}
    )
    assert Invitation.objects.filter(user=otherstudent, group=group).exists()
    assert Invitation.objects.filter(user=student, group=group).exists()
    assert response.status_code == 302

@pytest.mark.django_db
def test_invite_nonstudent_to_group(client, group, mentor, loggedInEducator):
    group.add_owner(loggedInEducator)
    response = client.post(
        reverse('groups:invite_to_group', kwargs={'group_id': group.id}),
        {'recipients': ", ".join([mentor.username])}
    )
    assert response.status_code == 200
    assert 'recipients' in response.context['form'].errors.keys()

@pytest.mark.django_db
def test_invite_nonexistant_to_group(client, group, student, loggedInEducator):
    group.add_owner(loggedInEducator)
    response = client.post(
        reverse('groups:invite_to_group', kwargs={'group_id': group.id}),
        {'recipients': ", ".join([student.username, 'nonexistant'])}
    )
    assert response.status_code == 200
    assert 'recipients' in response.context['form'].errors.keys()

@pytest.mark.django_db
def test_accept_invitation(client, group, loggedInStudent):
    group.invite_member(loggedInStudent)
    response = client.get(reverse('groups:accept_invitation', kwargs={'group_id': group.id}), HTTP_REFERER='/')
    assert len(group.members()) == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_reject_invitation(client, group, loggedInStudent):
    group.invite_member(loggedInStudent)
    response = client.get(reverse('groups:reject_invitation', kwargs={'group_id': group.id}))
    assert Invitation.objects.count() == 1
    assert response.status_code == 200
    response = client.post(reverse('groups:reject_invitation', kwargs={'group_id': group.id}))
    assert Invitation.objects.count() == 0
    assert response.status_code == 302

@pytest.mark.django_db
def test_create(client, loggedInEducator):
    response = client.post(reverse('groups:create'), {'name': "group1"},HTTP_REFERER='/')
    group = Group.objects.get(name='group1')
    assert len(group.owners()) == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_invite_member_sends_one_email(group, student):
    with mock.patch('groups.models.send') as send:
        group.invite_member(student)
        assert send.called
        assert send.call_count == 1

@pytest.mark.django_db
def test_invite_member_resends_one_email(group, student):
    with mock.patch('groups.models.send') as send:
        group.invite_member(student)
        group.invite_member(student)
        assert Invitation.objects.count() == 1
        assert send.called
        assert send.call_count == 2

@pytest.mark.django_db
def test_users_share_any_group(student, educator, group):
    group.add_owner(educator)
    group.add_member(student)
    assert Membership.users_share_any_group(educator.username, Role.owner, student.username, Role.member)
    assert not Membership.users_share_any_group(educator.username, Role.member, student.username, Role.member)
    assert not Membership.users_share_any_group(educator.username, Role.owner, student.username, Role.owner)
    assert not Membership.users_share_any_group(educator.username, Role.owner, 'nope', Role.member)

@pytest.mark.django_db
def test_owners_only_decorator(rf, group, student):
    group.add_owner(student)
    request = rf.get('/path')
    request.user = student
    view = mock.Mock()
    response = decorators.owners_only(view)(request, group_id=group.id)
    assert view.called

@pytest.mark.django_db
def test_owners_only_decorator_rejects_non_owners(rf, group, student):
    group.add_member(student)
    request = rf.get('/path')
    request.user = student
    view = mock.Mock()
    with pytest.raises(PermissionDenied):
        response = decorators.owners_only(view)(request, group_id=group.id)
    assert not view.called

@pytest.mark.django_db
def test_cascading_delete_for_members(student, educator, group):
    group.add_owner(educator)
    group.add_member(student)
    assert Membership.objects.count() == 2
    group.delete()
    assert Membership.objects.count() == 0

@pytest.mark.django_db
def test_cascading_delete_for_invited_members(student, educator, group):
    group.invite_member(student)
    assert Invitation.objects.count() == 1
    group.delete()
    assert Invitation.objects.count() == 0

@pytest.mark.django_db
def test_orphan_groups(student, educator, mentor, group):
    group.add_owner(educator)
    group.add_owner(mentor)
    group.add_member(student)
    assert Membership.objects.count() == 3

    group.delete_owner(mentor)
    assert Membership.objects.count() == 2
    assert Group.objects.count() == 1

    group.delete_owner(educator)
    assert Group.objects.count() == 0
    assert Membership.objects.count() == 0