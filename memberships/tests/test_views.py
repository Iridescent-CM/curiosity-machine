import pytest
from django.core.urlresolvers import reverse

from memberships.factories import MembershipFactory
from profiles.factories import EducatorFactory

@pytest.mark.django_db
def test_membership_detail_view_context_data(client):
    membership = MembershipFactory()
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get(reverse('memberships:membership', kwargs= {"membership_id": membership.id}), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership

@pytest.mark.django_db
def test_membership_challenge_list_view_context_data(client):
    membership = MembershipFactory()
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get(reverse('memberships:membership_challenges', kwargs= {"membership_id": membership.id}), follow=True)

    assert response.status_code == 200

    assert "membership" in response.context
    assert response.context["membership"] == membership
    assert "challenges" in response.context