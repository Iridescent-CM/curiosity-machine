import pytest
import os

from memberships.factories import MembershipFactory
from profiles.factories import UserFactory

from django.core.urlresolvers import reverse

TEST_DIR = os.path.dirname(__file__)

@pytest.mark.django_db
def test_get_import_members_renders_template_with_membership_and_form(client):
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

@pytest.mark.django_db
def test_post_import_members_with_errors_renders_template_with_errors_in_context(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.post(reverse("admin:import_members", kwargs={
        "id": membership.id
    }), {}, follow = False)

    assert response.status_code == 200
    assert response.templates[0].name == "memberships/admin/import_members/form.html"
    assert "errors" in response.context
    assert len(response.context['errors']) > 0

@pytest.mark.django_db
def test_post_import_members_with_file_puts_file_on_s3(client):
    pytest.fail("not yet written")

@pytest.mark.django_db
def test_post_import_members_with_file_redirects_to_processing_view_with_query_param(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    with open(os.path.join(TEST_DIR, './data/normal.csv')) as fp:
        client.login(username=user.username, password="123123")
        response = client.post(reverse("admin:import_members", kwargs={
            "id": membership.id
        }), {
            "csv_file": fp
        }, follow = False)

    assert response.status_code == 302
    assert response.url.endswith("%s?%s=%s" % (
        reverse("admin:process_member_import", kwargs={"id": membership.id}),
        "csv",
        "tbd" # FIXME
    ))

@pytest.mark.django_db
def test_get_process_member_import_renders_template_with_membership(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.get("%s?%s=%s" % (
        reverse("admin:process_member_import", kwargs={ "id": membership.id }),
        "csv",
        "fake-file-url"
    ))

    assert response.status_code == 200
    assert response.context["original"] == membership
    assert response.templates[0].name == "memberships/admin/import_members/process.html"

@pytest.mark.django_db
def test_get_process_member_import_has_admin_context_variables(client):
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)
    membership = MembershipFactory()

    client.login(username=user.username, password="123123")
    response = client.get("%s?%s=%s" % (
        reverse("admin:process_member_import", kwargs={ "id": membership.id }),
        "csv",
        "fake-file-url"
    ))

    assert response.status_code == 200
    assert "opts" in response.context
    assert "site_url" in response.context
    assert "site_title" in response.context
    assert "site_header" in response.context
