import pytest

from challenges.factories import ChallengeFactory, ProgressFactory
from profiles.factories import UserFactory, MentorFactory, EducatorFactory, ParentFactory, ParentConnectionFactory, StudentFactory
from memberships.factories import MembershipFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_anonymous_user_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)

    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=True)

    assert response.status_code == 200
    assert "registration/login.html" == response.templates[0].name

@pytest.mark.django_db
def test_allows_staff(client):
    progress = ProgressFactory()
    user = UserFactory(is_staff=True, username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_allows_mentor(client):
    progress = ProgressFactory()
    user = MentorFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_allows_current_user(client):
    progress = ProgressFactory()

    client.login(username=progress.student.username, password="123123")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_connected_educator_access_granted(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')
    MembershipFactory(members=[progress.student, educator])

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_unconnected_educator_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))

@pytest.mark.django_db
def test_connected_parent_access_granted(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    parent = ParentFactory(username='user', password='123123')
    ParentConnectionFactory(parent_profile=parent.profile, child_profile=progress.student.profile, active=True)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_unconnected_parent_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    parent = ParentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))

@pytest.mark.django_db
def test_allows_educator_sharing_membership(client):
    progress = ProgressFactory()
    user = EducatorFactory(username="username", password="password")
    MembershipFactory(members=[progress.student, user])

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_allows_parent_sharing_membership(client):
    progress = ProgressFactory()
    user = ParentFactory(username="username", password="password")
    MembershipFactory(members=[progress.student, user])

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_does_not_allow_other_student(client):
    progress = ProgressFactory()
    user = StudentFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={"challenge_id": progress.challenge.id}))

