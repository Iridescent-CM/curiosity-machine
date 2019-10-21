from django.http import HttpResponseRedirect
from django.urls import reverse
from profiles.factories import *
from ..factories import *
import pytest

@pytest.mark.django_db
def test_completes(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user)
    setattr(settings, "SURVEY_%s_LINK" % sr.survey_id, "link")
    assert sr.unknown

    client.login(username='username', password='password')
    qparams = "?%s=%s" % (settings.SURVEYMONKEY_TOKEN_VAR, sr.id)
    client.get(
        reverse("surveys:survey_completed") + qparams
    )
    sr.refresh_from_db()
    assert sr.completed

@pytest.mark.django_db
def test_completes_with_old_style_url(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user)
    setattr(settings, "SURVEY_%s_LINK" % sr.survey_id, "link")
    assert sr.unknown

    client.login(username='username', password='password')
    qparams = "?%s=%s" % (settings.SURVEYMONKEY_TOKEN_VAR, sr.id)
    client.get(
        "/surveys/SOME_PK/completed/" + qparams
    )
    sr.refresh_from_db()
    assert sr.completed

@pytest.mark.django_db
def test_redirects_as_configured(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    settings.SURVEY_987_REDIRECT="logout"
    settings.SURVEY_987_LINK="link"

    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user, survey_id=987)

    client.login(username='username', password='password')
    qparams = "?%s=%s" % (settings.SURVEYMONKEY_TOKEN_VAR, sr.id)
    response = client.get(
        reverse("surveys:survey_completed") + qparams
    )
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("logout")

@pytest.mark.django_db
def test_sets_message_as_configured(client, settings):
    settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS=False
    settings.SURVEY_987_MESSAGE="great job everybody"
    settings.SURVEY_987_LINK="link"

    user = UserFactory(username='username', password='password')
    sr = SurveyResponseFactory(user=user, survey_id=987)

    client.login(username='username', password='password')
    qparams = "?%s=%s" % (settings.SURVEYMONKEY_TOKEN_VAR, sr.id)
    response = client.get(
        reverse("surveys:survey_completed") + qparams,
        follow=True
    )
    assert "great job everybody" in response.content.decode('utf-8')
