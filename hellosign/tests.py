import mock
import pytest

from . import ConsentTemplate

def test_consent_template():
    with mock.patch('hellosign.settings') as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_X = "whatever"

        assert ConsentTemplate("123")
        assert ConsentTemplate("123").name == "SOME_NAME"
        assert ConsentTemplate("123").x == "whatever"
