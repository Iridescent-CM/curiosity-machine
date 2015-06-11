import pytest
import mock
from profiles import forms, models
from django.contrib.auth.models import User

def test_form_required_fields_on_creation():
    f = forms.mentor.MentorUserAndProfileForm()

    required = ['username', 'email', 'password', 'confirm_password', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_change_form_required_fields_on_edit():
    user = User()
    profile = models.Profile()
    profile.user = user
    f = forms.mentor.MentorUserAndProfileChangeForm(instance=user)

    required = ['email', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_mentor_join_form_clean_passwords_match():
    f = forms.mentor.MentorUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '456456'
    })
    assert 'password' in f.errors
    assert 'do not match' in f.errors['password'].as_text()

def test_mentor_join_form_clean_password_strength():
    f = forms.mentor.MentorUserAndProfileForm(data={
        'password': 'hi'
    })
    assert 'password' in f.errors
    assert 'must be at least 6 characters long' in f.errors['password'].as_text()

def test_mentor_join_form_clean_username_illegal_characters():
    f = forms.mentor.MentorUserAndProfileForm(data={
        'username': 'me!'
    })
    assert 'username' in f.errors
    assert 'can only include' in f.errors['username'].as_text()

