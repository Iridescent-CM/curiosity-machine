import pytest

from memberships.factories import MembershipFactory
from profiles.factories import UserFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_get_import_members_renders_template_with_membership(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:import_members", kwargs={
        "id": membership.id
    }))

    assert response.status_code == 200
    assert response.templates[0].name == "memberships/admin/import_members/form.html"
    assert response.context["original"] == membership

@pytest.mark.django_db
def test_get_import_members_context_has_admin_stuff(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:import_members", kwargs={
        "id": membership.id
    }))

    assert response.status_code == 200
    assert "opts" in response.context
    assert "site_url" in response.context
    assert "site_title" in response.context
    assert "site_header" in response.context
