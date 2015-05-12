import pytest
import mock
from profiles import forms

def test_require_fields():
    f = forms.parent.ParentUserAndProfileForm()

    required = ['username', 'email', 'password', 'confirm_password', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
        else:
            assert not field.required, "%s should not be required and is" % name

@pytest.mark.django_db
def test_creates_user_with_profile():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    assert f.is_valid()
    user = f.save()
    assert hasattr(user, "profile")

@pytest.mark.django_db
def test_sets_is_parent_flag():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    user = f.save()
    assert user.profile.is_parent
    
