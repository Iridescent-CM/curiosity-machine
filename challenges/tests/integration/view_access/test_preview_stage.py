import pytest
from challenges.factories import ChallengeFactory
from django.urls import reverse
from educators.factories import EducatorFactory
from memberships.factories import MembershipFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_requires_login(client):
    challenge = ChallengeFactory()

    response = client.get(reverse("challenges:preview_plan", kwargs={"challenge_id": challenge.id}))
    assert response.status_code == 302
    assert 'login/?next' in response.url

@pytest.mark.django_db
def test_allows_all_on_free_challenge(client):
    free_challenge = ChallengeFactory(free=True)

    for i, Factory in enumerate([EducatorFactory, StudentFactory]):
        user = Factory(username='username%d' % i, password='password')

        client.login(username='username%d' % i, password='password')
        response = client.get(reverse("challenges:preview_plan", kwargs={"challenge_id": free_challenge.id}))

        assert response.status_code == 200

@pytest.mark.django_db
def test_allows_all_with_membership_connection(client):
    challenge = ChallengeFactory(free=False)

    for i, Factory in enumerate([EducatorFactory, StudentFactory]):
        user = Factory(username='username%d' % i, password='password')
        membership = MembershipFactory(members=[user], challenges=[challenge])

        client.login(username='username%d' % i, password='password')
        response = client.get(reverse("challenges:preview_plan", kwargs={"challenge_id": challenge.id}))

        assert response.status_code == 200

@pytest.mark.django_db
def test_does_not_allow_others_with_no_connection_on_non_free(client):
    challenge = ChallengeFactory(free=False)

    for i, Factory in enumerate([EducatorFactory, StudentFactory]):
        user = Factory(username='username%d' % i, password='password')

        client.login(username='username%d' % i, password='password')
        response = client.get(reverse("challenges:preview_plan", kwargs={"challenge_id": challenge.id}))

        assert response.status_code == 403
