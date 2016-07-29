import pytest

from challenges.factories import ChallengeFactory
from profiles.factories import StudentFactory, MentorFactory, EducatorFactory, ParentFactory
from memberships.factories import MembershipFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_start_building_is_student_only(client):
    challenge = ChallengeFactory(free=True)

    # student can start building a free challenge
    student = StudentFactory(username="username", password="password")
    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={
        "challenge_id": challenge.id, "username": student.username
    }))

    # other user roles can't
    mentor = MentorFactory(username="username1", password="password")
    client.login(username="username1", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

    mentor = EducatorFactory(username="username2", password="password")
    client.login(username="username2", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

    mentor = ParentFactory(username="username3", password="password")
    client.login(username="username3", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

@pytest.mark.django_db
def test_start_building_enforces_membership_access_rules(client):
    challenge = ChallengeFactory(free=False)

    # student can't start building a non-free challenge...
    student = StudentFactory(username="username", password="password")
    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

    # ...without connection through membership
    membership = MembershipFactory(members=[student], challenges=[challenge])
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={
        "challenge_id": challenge.id, "username": student.username
    }))