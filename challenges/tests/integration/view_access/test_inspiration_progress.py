import pytest
from challenges.factories import ChallengeFactory, ProgressFactory
from django.core.urlresolvers import reverse
from educators.factories import EducatorFactory
from memberships.factories import MembershipFactory
from mentors.factories import MentorFactory
from profiles.factories import UserFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_anonymous_user_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)

    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.owner.username), follow=True)

    assert response.status_code == 200
    assert "account/login.html" == response.templates[0].name

@pytest.mark.django_db
def test_allows_staff(client):
    progress = ProgressFactory()
    user = UserFactory(is_staff=True, username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_allows_mentor(client):
    progress = ProgressFactory()
    user = MentorFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_allows_current_user(client):
    progress = ProgressFactory()

    client.login(username=progress.owner.username, password="123123")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_connected_educator_access_granted(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')
    MembershipFactory(members=[progress.owner, educator])

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_unconnected_educator_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))

@pytest.mark.django_db
def test_allows_educator_sharing_membership(client):
    progress = ProgressFactory()
    user = EducatorFactory(username="username", password="password")
    MembershipFactory(members=[progress.owner, user])

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_does_not_allow_other_student(client):
    progress = ProgressFactory()
    user = StudentFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/%d/%s/inspiration/' % (progress.challenge.id, progress.owner.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={"challenge_id": progress.challenge.id}))

