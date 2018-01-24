import mock
import pytest
from students.factories import *
from .models import *

def test_consent_template():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_X = "whatever"

        assert ConsentTemplate("123")
        assert ConsentTemplate("123").name == "SOME_NAME"
        assert ConsentTemplate("123").x == "whatever"

def test_signature_custom_fields():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build(studentprofile__birthday="2000-01-01")

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_EMAIL_ID = "abc"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_USERNAME_ID = "def"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_BIRTHDAY_ID = "ghi"

        sig = Signature(template_id="123", user=user)
        assert sig.get_custom_fields() == [{
            "abc": user.email,
            "def": user.username,
            "ghi": "Jan 01, 2000"
        }]

def test_signature_custom_fields_omitted_id():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        user = StudentFactory.build()

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_EMAIL_ID = "abc"

        sig = Signature(template_id="123", user=user)
        assert sig.get_custom_fields() == [{
            "abc": user.email,
        }]

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

def test_template_active():
    with mock.patch('hellosign.models.settings', spec=True) as settings:
        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ID = "123"
        assert not ConsentTemplate("123").active

        settings.HELLOSIGN_TEMPLATE_SOME_NAME_ACTIVE = 1
        assert ConsentTemplate("123").active
