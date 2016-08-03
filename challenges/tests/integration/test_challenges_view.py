import pytest

from challenges.tests.fixtures import *
from profiles.tests import student, mentor

from django.contrib.auth.models import AnonymousUser
from challenges.factories import ChallengeFactory

from challenges.views import challenges

@pytest.mark.django_db
def test_challenges_accessible_to_anonymous_user(rf, challenge, student):
    request = rf.get('/challenges/')
    request.user = AnonymousUser()
    response = challenges(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenges_render_challenges(client, challenge, student):
    response = client.get('/challenges/', follow=True)
    assert response.status_code == 200
    assert response.context['challenges'][0] == challenge

@pytest.mark.django_db
def test_challenges_filters_by_name(client, challenge, challenge2, theme, student):
    challenge.themes.add(theme)
    challenge.save()

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    response = client.get('/challenges/', {'theme': theme.name}, follow=True)
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_challenges_filters_drafts(client, challenge, challenge2, student):
    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    challenge.draft = True
    challenge.save()

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_challenges_decorates_with_membership_accessibility(client):
    ChallengeFactory(draft=False)
    ChallengeFactory(draft=False, free=True)

    response = client.get('/challenges/')
    assert set([c.accessible for c in response.context['challenges']]) == set([True, False])
