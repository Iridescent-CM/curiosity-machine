import mock
import pytest
from profiles.factories import *
from ..models import *

def test_status_attrs():
    # pick a few examples, assume the implementation handles all status values
    assert SurveyResponse(status=ResponseStatus.UNKNOWN).unknown
    assert not SurveyResponse(status=ResponseStatus.UNKNOWN).completed
    assert SurveyResponse(status=ResponseStatus.COMPLETED).completed

def test_surveyresponse_facade_over_survey(settings):
    settings.SURVEY_123_ACTIVE = "1"
    settings.SURVEY_123_LINK = "link"

    assert SurveyResponse(survey_id="123").active
    assert SurveyResponse(survey_id="123").link == "link"

@pytest.mark.django_db
def test_survey_response_url(settings):
    settings.SURVEY_123_LINK = "http://mywebsite.biz"
    settings.SURVEY_123_URL = "cant_clobber"

    user = UserFactory()

    sr = SurveyResponse(survey_id="123", user=user)
    assert sr.url == "http://mywebsite.biz?cmtoken=%s&uid=%s" % (sr.id, user.id)

@pytest.mark.django_db
def test_survey_response_url_with_query_params(settings):
    settings.SURVEY_123_LINK = "http://mywebsite.biz?some=query&params=already"
    user = UserFactory()

    sr = SurveyResponse(survey_id="123", user=user)
    assert sr.url == "http://mywebsite.biz?some=query&params=already&cmtoken=%s&uid=%s" % (sr.id, user.id)
