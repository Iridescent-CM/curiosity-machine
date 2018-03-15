import mock
import pytest
from ..models import *

class SomeConsentTemplate(ConsentTemplate):
    """
    Used later in test(s)
    """
    pass

def test_consent_template_is_abstract():
    with pytest.raises(TypeError):
        ConsentTemplate()

def test_find_name():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"

        assert ConsentTemplate.find_name("123") == "SOME_NAME"

def test_find_setting():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_X = "whatever"

        assert ConsentTemplate.find_setting("SOME_NAME", "x") == "whatever"

def test_lookup_instance_default():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"

        assert isinstance(ConsentTemplate.lookup_instance("123"), GenericConsentTemplate)

def test_lookup_instance_custom_class():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_CLASS = "hellosign.tests.test_consent_template.SomeConsentTemplate"

        assert isinstance(ConsentTemplate.lookup_instance("123"), SomeConsentTemplate)

def test_generic_consent_template():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_X = "whatever"

        assert GenericConsentTemplate("123")
        assert GenericConsentTemplate("123").name == "SOME_NAME"
        assert GenericConsentTemplate("123").x == "whatever"

def test_template_active():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        assert not GenericConsentTemplate("123").active

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ACTIVE = 1
        assert GenericConsentTemplate("123").active
