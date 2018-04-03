from django.urls import reverse
from profiles.factories import *
from ..factories import *
import pytest

@pytest.mark.django_db
def test_completes(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user)
    assert sr.unknown

    client.login(username='username', password='password')
    client.get(
        reverse("surveys:survey_completed", kwargs={"survey_pk": sr.survey_id}),
        HTTP_REFERER="https://www.surveymonkey.com/r/ABCD123"
    )
    sr.refresh_from_db()
    assert sr.completed

@pytest.mark.django_db
def test_no_referer(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user)

    client.login(username='username', password='password')
    client.get(
        reverse("surveys:survey_completed", kwargs={"survey_pk": sr.survey_id}),
        # no HTTP_REFERER
    )
    sr.refresh_from_db()
    assert sr.unknown
