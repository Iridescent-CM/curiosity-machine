import pytest
from django.urls import reverse
from profiles.models import UserExtra
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
def test_get_sets_hidden_field(client):
    response = client.get(reverse("account_signup", kwargs={"source": "test_source"})) 
    doc = pq(response.content)
    inp = doc('input[type="hidden"][name="source"]')
    assert inp
    assert inp.val() == 'test_source'

@pytest.mark.django_db
def test_post_with_source_sets_source(client):
    client.post(reverse("account_signup"), signup_formdata())
    assert UserExtra.objects.filter(source="test_source", user__username="test").count() == 1

@pytest.mark.django_db
def test_post_to_source_url_sets_source(client):
    client.post(reverse("account_signup", kwargs={"source": "test_source"}), signup_formdata())
    assert UserExtra.objects.filter(source="test_source", user__username="test").count() == 1
