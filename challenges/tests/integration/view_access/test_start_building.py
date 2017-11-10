import pytest
from challenges.factories import ChallengeFactory
from django.core.urlresolvers import reverse
from educators.factories import EducatorFactory
from memberships.factories import MembershipFactory
from mentors.factories import MentorFactory
from parents.factories import ParentFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_does_not_allow_mentors(client):
    challenge = ChallengeFactory(free=True)
    mentor = MentorFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))

    assert response.status_code == 403

@pytest.mark.django_db
def test_does_not_allow_educators(client):
    challenge = ChallengeFactory(free=True)
    educator = EducatorFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))

    assert response.status_code == 403

@pytest.mark.django_db
def test_does_not_allow_parents(client):
    parent = ParentFactory(username="username", password="password")
    challenge = ChallengeFactory(free=True)

    client.login(username="username", password="password")

    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

@pytest.mark.django_db
def test_allows_students_on_free_challenges(client):
    challenge = ChallengeFactory(free=True)
    student = StudentFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={
        "challenge_id": challenge.id, "username": student.username
    }))

@pytest.mark.django_db
def test_allows_students_with_membership_connection(client):
    student = StudentFactory(username="username", password="password")
    challenge = ChallengeFactory(free=False)
    membership = MembershipFactory(members=[student], challenges=[challenge])

    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={
        "challenge_id": challenge.id, "username": student.username
    }))

@pytest.mark.django_db
def test_does_not_allow_student_without_membership_connection_on_non_free_challenge(client):
    student = StudentFactory(username="username", password="password")
    challenge = ChallengeFactory(free=False)

    client.login(username="username", password="password")
    response = client.post(reverse("challenges:start_building", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 403

