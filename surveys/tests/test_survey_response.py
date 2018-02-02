import mock
import pytest
from ..models import *

def test_status_attrs():
    # pick a few examples, assume the implementation handles all status values
    assert SurveyResponse(status=ResponseStatus.UNKNOWN).unknown
    assert not SurveyResponse(status=ResponseStatus.UNKNOWN).completed
    assert SurveyResponse(status=ResponseStatus.COMPLETED).completed

def test_surveyresponse_facade_over_survey():
    with mock.patch('surveys.settings') as settings:
        settings.SURVEY_123_ACTIVE = "1"
        settings.SURVEY_123_LINK = "link"

        assert SurveyResponse(survey_id="123").active
        assert SurveyResponse(survey_id="123").link == "link"

def test_survey_response_url():
    with mock.patch('surveys.settings') as settings:
        settings.SURVEY_123_LINK = "link"
        settings.SURVEY_123_URL = "cant_clobber"

        sr = SurveyResponse(survey_id="123")
        assert sr.url == "link?cmtoken=%s" % sr.id
