import pytest
from django.core.urlresolvers import reverse

from memberships.factories import *
from profiles.factories import *
from challenges.factories import *

@pytest.mark.django_db
def test_membership_detail_view_context_data(client):
    educator = EducatorFactory(username="edu", password="123123")
    membership = MembershipFactory(members=[educator])

    client.login(username="edu", password="123123")
    response = client.get(reverse('memberships:membership', kwargs= {"membership_id": membership.id}), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership

@pytest.mark.django_db
def test_membership_challenge_list_view_context_data(client):
    educator = EducatorFactory(username="edu", password="123123")
    membership = MembershipFactory(members=[educator])

    client.login(username="edu", password="123123")
    response = client.get(reverse('memberships:membership_challenges', kwargs= {"membership_id": membership.id}), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership
    assert "challenges" in response.context

@pytest.mark.django_db
def test_membership_challenge_detail_view_context_data(client):
    student = StudentFactory()
    educator = EducatorFactory(username="edu", password="123123")

    challenge = ChallengeFactory()
    progress1 = ProgressFactory(student=student, challenge=challenge)
    progress2 = ProgressFactory()

    membership = MembershipFactory(challenges=[challenge], members=[student, educator])

    client.login(username="edu", password="123123")
    response = client.get(reverse(
        'memberships:membership_challenge',
        kwargs= {
            "membership_id": membership.id,
            "challenge_id": challenge.id
        }
    ), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership

    assert "challenge" in response.context
    assert response.context["challenge"] == challenge

    assert "progresses" in response.context
    assert set(response.context["progresses"]) == set([progress1])
    assert hasattr(response.context["progresses"][0], "student_reflect_comments")

@pytest.mark.django_db
def test_membership_student_list_view_context_data(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory()
    membership = MembershipFactory(members=[educator, student])

    client.login(username="edu", password="123123")
    response = client.get(reverse('memberships:membership_students', kwargs= {"membership_id": membership.id}), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership
    assert "students" in response.context
    assert set(response.context["students"]) == set([student])

@pytest.mark.django_db
def test_membership_student_detail_view_context_data(client):
    student = StudentFactory()
    progress1 = ProgressFactory(student=student)
    progress2 = ProgressFactory()
    educator = EducatorFactory(username="edu", password="123123")

    membership = MembershipFactory(members=[educator, student])

    client.login(username="edu", password="123123")
    response = client.get(reverse(
        'memberships:membership_student',
        kwargs= {
            "membership_id": membership.id,
            "student_id": student.id
        }
    ), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership
    assert "student" in response.context
    assert response.context["student"] == student
    assert "progresses" in response.context
    assert set(response.context["progresses"]) == set([progress1])