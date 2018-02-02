import mock
import pytest
from ..models import *

def test_consent_template():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_X = "whatever"

        assert ConsentTemplate("123")
        assert ConsentTemplate("123").name == "SOME_NAME"
        assert ConsentTemplate("123").x == "whatever"

def test_template_active():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        assert not ConsentTemplate("123").active

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ACTIVE = 1
        assert ConsentTemplate("123").active
