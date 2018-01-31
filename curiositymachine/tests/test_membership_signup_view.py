import pytest
from django.urls import reverse
from memberships.factories import *
from pyquery import PyQuery as pq

def signup_formdata(**kwargs):
    return dict({
        "username": "test",
        "password1": "password",
        "password2": "password",
        "email": "email@email.com",
        "source": "test_source"
    }, **kwargs)

@pytest.mark.django_db
def test_get_includes_membership_name(client):
    membership = MembershipFactory(slug="myslug")
    response = client.get(reverse("membership_signup", kwargs={"slug": "myslug"}))
    doc = pq(response.content)
    head = doc('h1')
    assert head
    assert membership.display_name in head.text()

@pytest.mark.django_db
def test_post_creates_member(client):
    membership = MembershipFactory(slug="myslug")
    assert membership.members.count() == 0
    client.post(reverse("membership_signup", kwargs={"slug": "myslug"}), signup_formdata())
    assert membership.members.count() == 1

@pytest.mark.django_db
def test_slug_matches_any_case(client):
    membership = MembershipFactory(slug="myslug")
    assert client.get(reverse("membership_signup", kwargs={"slug": "myslug"})).status_code == 200
    assert client.get(reverse("membership_signup", kwargs={"slug": "MySlug"})).status_code == 200
    assert client.get(reverse("membership_signup", kwargs={"slug": "notmyslug"})).status_code == 404