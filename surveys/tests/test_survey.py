import mock
import pytest
from .. import get_survey

def test_get_survey():
    with mock.patch('surveys.settings') as settings:
        settings.SURVEY_123_ACTIVE = "1"
        settings.SURVEY_123_LINK = "link"

        assert get_survey("123")
        assert get_survey("123").active
        assert get_survey("123").link == "link"
