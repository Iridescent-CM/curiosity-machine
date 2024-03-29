import mock
import pytest
from mock import sentinel
from students.factories import *
from ..models import *


class SomeConsentTemplate(ConsentTemplate):
    def get_custom_fields(self, *args):
        return sentinel.custom_fields_return

def test_signature_custom_fields():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build()

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_EMAIL_ID = "abc"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_USERNAME_ID = "def"

        sig = Signature(template_id="123", user=user)
        assert sig.get_custom_fields() == {
            "abc": user.email,
            "def": user.username,
        }

def test_signature_custom_fields_omitted_id():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build()

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_EMAIL_ID = "abc"

        sig = Signature(template_id="123", user=user)
        assert sig.get_custom_fields() == {
            "abc": user.email,
        }

def test_custom_fields_from_custom_template_class():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build()

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_EMAIL_ID = "abc"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_CLASS = "hellosign.tests.test_signature.SomeConsentTemplate"

        sig = Signature(template_id="123", user=user)
        assert isinstance(sig.template, SomeConsentTemplate)
        assert sig.get_custom_fields() == sentinel.custom_fields_return

def test_signature_signers():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build()

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"

        assert Signature(template_id="123", user=user).get_signers() == [{
            "name": user.username,
            "email_address": user.email,
            "role_name": "Parent"
        }]

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_SIGNER_ROLE = "Parent or guardian"
        assert Signature(template_id="123", user=user).get_signers()[0]["role_name"] == "Parent or guardian"
