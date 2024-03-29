import mock
import pytest
from .. import get_survey

def test_active_defaults_to_false():
    with mock.patch('surveys.settings', autospec=True) as settings:
        settings.SURVEY_123_LINK = "link"

        assert not get_survey("123").active

def test_get_survey():
    with mock.patch('surveys.settings', autospec=True) as settings:
        settings.SURVEY_123_ACTIVE = "1"
        settings.SURVEY_123_LINK = "link"

        assert get_survey("123")
        assert get_survey("123").active
        assert get_survey("123").link == "link"

def test_get_survey_is_case_insensitive():
    with mock.patch('surveys.settings', autospec=True) as settings:
        settings.SURVEY_SOME_SURVEY_ACTIVE = "1"
        settings.SURVEY_SOME_SURVEY_LINK = "link"

        assert get_survey("SOME_SURVEY").link == "link"
        assert get_survey("some_survey").link == "link"
