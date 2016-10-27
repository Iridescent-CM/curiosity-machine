import pytest

from challenges.tests.fixtures import *
from profiles.tests import student, mentor

from django.contrib.auth.models import AnonymousUser
from challenges.factories import *
from profiles.factories import *
from memberships.factories import *

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
def test_challenges_filters_by_theme_name(client, challenge, challenge2, theme, student):
    challenge.themes.add(theme)
    challenge.save()

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    response = client.get('/challenges/', {'theme': theme.name}, follow=True)
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_filters_by_membership(client):
    challenges = ChallengeFactory.create_batch(2, draft=False)
    user = UserFactory(username="username", password="password")
    membership = MembershipFactory(challenges=[challenges[0]], members=[user])

    client.login(username="username", password="password")

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert set(response.context['challenges']) == set(challenges)

    response = client.get('/challenges/', {'membership': membership.id})
    assert response.status_code == 200
    assert set(response.context['challenges']) == set(challenges[0:1])

@pytest.mark.django_db
def test_redirects_to_login_for_anonymous(client):
    membership = MembershipFactory()

    response = client.get('/challenges/', {'membership': membership.id})
    assert response.status_code == 302

@pytest.mark.django_db
def test_redirects_on_non_existant_membership(client):
    user = UserFactory(username="username", password="password")

    client.login(username="username", password="password")
    response = client.get('/challenges/', {'membership': 1})
    assert response.status_code == 302

@pytest.mark.django_db
def test_404s_on_non_int_query_params(client):
    client.login(username="username", password="password")

    response = client.get('/challenges/', {'membership': 'x'})
    assert response.status_code == 404

    response = client.get('/challenges/', {'filter_id': 'x'})
    assert response.status_code == 404

@pytest.mark.django_db
def test_redirects_on_non_user_membership(client):
    challenges = ChallengeFactory.create_batch(2, draft=False)
    user = UserFactory(username="username", password="password")
    membership = MembershipFactory(challenges=[challenges[0]])

    client.login(username="username", password="password")
    response = client.get('/challenges/', {'membership': membership.id})
    assert response.status_code == 302

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

@pytest.mark.django_db
def test_challenges_decorates_with_started_for_student(client):
    c1 = ChallengeFactory(draft=False)
    c2 = ChallengeFactory(draft=False)
    user = StudentFactory(username="user", password="password")
    p = ProgressFactory(challenge=c2, student=user)

    client.login(username="user", password="password")
    response = client.get('/challenges/')
    assert {c.id: c.started for c in response.context['challenges']} == { c1.id: False, c2.id: True }

@pytest.mark.django_db
def test_challenges_decorates_has_resources_for_non_student_users(client):
    c1 = ChallengeFactory(draft=False)
    c2 = ChallengeFactory(draft=False)
    user = EducatorFactory(username="user", password="password")

    client.login(username="user", password="password")
    response = client.get('/challenges/')
    for challenge in response.context['challenges']:
        assert hasattr(challenge, 'has_resources')

@pytest.mark.django_db
def test_challenges_does_not_decorate_has_resources_for_student_or_anonymous(client):
    c1 = ChallengeFactory(draft=False)
    c2 = ChallengeFactory(draft=False)
    user = StudentFactory(username="user", password="password")

    response = client.get('/challenges/')
    for challenge in response.context['challenges']:
        assert not hasattr(challenge, 'has_resources')

    client.login(username="user", password="password")
    response = client.get('/challenges/')
    for challenge in response.context['challenges']:
        assert not hasattr(challenge, 'has_resources')

@pytest.mark.django_db
def test_shows_filter_header_template(client):
    f = FilterFactory(header_template='challenges/filters/test.html')
    response = client.get('/challenges/', {"filter_id": f.id})

    assert b'test header_template' in response.content
