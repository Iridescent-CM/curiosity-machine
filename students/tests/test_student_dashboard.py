import pytest

from challenges.factories import *
from django.core.urlresolvers import reverse
from memberships.factories import *
from students.factories import *

@pytest.mark.django_db
def test_dashboard_includes_memberships(client):
    student = StudentFactory(username="user", password="password")
    memberships = MembershipFactory.create_batch(2, members=[student])

    client.login(username="user", password="password")
    response = client.get(reverse("students:home"))

    assert response.status_code == 200
    assert set(response.context["memberships"]) == set(memberships)

@pytest.mark.django_db
def test_dashboard_skips_inactive_memberships(client):
    student = StudentFactory(username="user", password="password")
    membership = MembershipFactory(members=[student], is_active=False)

    client.login(username="user", password="password")
    response = client.get(reverse("students:home"))

    assert response.status_code == 200
    assert not response.context["memberships"]

@pytest.mark.django_db
def test_membership_filter_404s_on_bad_query_parameter(client):
    student = StudentFactory(username="user", password="password")

    client.login(username="user", password="password")
    response = client.get(reverse("students:home") + "?membership=x")

    assert response.status_code == 404

@pytest.mark.django_db
def test_membership_filter_includes_membership_challenges(client):
    student = StudentFactory(username="user", password="password")
    challenges = ChallengeFactory.create_batch(3)
    membership = MembershipFactory(challenges=challenges, members=[student])

    client.login(username="user", password="password")
    response = client.get(reverse("students:home") + "?membership=%d" % membership.id)

    assert response.status_code == 200
    assert response.context["selected_membership"] == membership.id
    assert set(response.context["selected_membership_challenges"]) == set(challenges)

@pytest.mark.django_db
def test_membership_filter_shows_no_challenges_on_non_member_membership(client):
    student = StudentFactory(username="user", password="password")
    challenges = ChallengeFactory.create_batch(3)
    membership = MembershipFactory(challenges=challenges)

    client.login(username="user", password="password")
    response = client.get(reverse("students:home") + "?membership=%d" % membership.id)

    assert response.status_code == 200
    assert not response.context["selected_membership_challenges"]