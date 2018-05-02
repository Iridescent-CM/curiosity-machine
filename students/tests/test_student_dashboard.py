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
    response = client.get(reverse("students:home"), follow=True)

    assert response.status_code == 200
    assert set(response.context["memberships"]) == set(memberships)

@pytest.mark.django_db
def test_dashboard_skips_inactive_memberships(client):
    student = StudentFactory(username="user", password="password")
    membership = MembershipFactory(members=[student], is_active=False)

    client.login(username="user", password="password")
    response = client.get(reverse("students:home"), follow=True)

    assert response.status_code == 200
    assert not response.context["memberships"]

@pytest.mark.django_db
def test_membership_challenges_404s_on_bad_id(client):
    student = StudentFactory(username="user", password="password")

    client.login(username="user", password="password")
    response = client.get(reverse("students:membership", kwargs={'membership_id': 2}))

    assert response.status_code == 404