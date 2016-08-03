import pytest

from challenges.factories import ChallengeFactory
from profiles.factories import StudentFactory, MentorFactory, ParentFactory, EducatorFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_anonymous_can_access(client):
    challenge = ChallengeFactory()

    response = client.get(reverse("challenges:preview_inspiration", kwargs={"challenge_id": challenge.id}))

    assert response.status_code == 200

@pytest.mark.django_db
def test_all_roles_can_access(client):
    challenge = ChallengeFactory()

    for i, Factory in enumerate([StudentFactory, MentorFactory, EducatorFactory, ParentFactory]):
        user = Factory(username="username%d" % i, password="password")

        client.login(username="username%d" % i, password="password")
        response = client.get(reverse("challenges:preview_inspiration", kwargs={"challenge_id": challenge.id}))

        assert response.status_code == 200, "user from factory idx %d failed" % i
