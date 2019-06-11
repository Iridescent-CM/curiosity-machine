import pytest
from challenges.factories import ProgressFactory
from django.core.urlresolvers import reverse
from educators.factories import EducatorFactory
from memberships.factories import MembershipFactory
from profiles.factories import UserFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_requires_login(client):
    progress = ProgressFactory()

    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))
    assert response.status_code == 302
    assert 'login/?next' in response.url

@pytest.mark.django_db
def test_allows_staff(client):
    progress = ProgressFactory()
    user = UserFactory(is_staff=True, username="username", password="password")

    client.login(username="username", password="password")
    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username, "stage": "plan"}))

@pytest.mark.django_db
def test_allows_current_user(client):
    progress = ProgressFactory()

    client.login(username=progress.owner.username, password="123123")
    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username, "stage": "plan"}))

@pytest.mark.django_db
def test_allows_educator_sharing_membership(client):
    progress = ProgressFactory()
    user = EducatorFactory(username="username", password="password")
    MembershipFactory(members=[progress.owner, user])

    client.login(username="username", password="password")
    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username, "stage": "plan"}))

@pytest.mark.django_db
def test_does_not_allow_other_student(client):
    progress = ProgressFactory()
    user = StudentFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={"challenge_id": progress.challenge.id}))

@pytest.mark.django_db
def test_does_not_allow_other_educator(client):
    progress = ProgressFactory()
    user = EducatorFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get(reverse("challenges:challenge_progress", kwargs={"challenge_id": progress.challenge.id, "username": progress.owner.username}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={"challenge_id": progress.challenge.id}))
