import pytest

from memberships.factories import MembershipFactory
from profiles.factories import UserFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_import_members_view_renders_template_with_membership_and_form(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:import_members", kwargs={
        "id": membership.id
    }))

    assert response.status_code == 200
    assert response.templates[0].name == "memberships/admin/import_members/form.html"
    assert response.context["original"] == membership
    assert "form" in response.context

@pytest.mark.django_db
def test_get_import_members_has_admin_context_variables(client):
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
    assert "adminform" in response.context
    assert hasattr(response.context["adminform"], "fieldsets")
