import pytest
import mock
from datetime import datetime
from profiles import forms, models
from django.contrib.auth.models import User

def test_form_required_fields_on_creation():
    f = forms.parent.ParentUserAndProfileForm()

    required = ['username', 'email', 'password', 'confirm_password', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_form_required_fields_on_edit():
    user = User()
    profile = models.Profile()
    profile.user = user
    f = forms.parent.ParentUserAndProfileForm(instance=user)

    required = ['email', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

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
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

@pytest.mark.django_db
def test_modifies_exisiting_user_and_profile():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity',
        'is_student': True
    })
    user = f.save()
    f = forms.parent.ParentUserAndProfileForm(
        instance=user,
        data={
            'email': 'new@example.com',
            'city': 'newcity'
        }
    )
    user = f.save()
    assert user.email == 'new@example.com'
    assert user.profile.city == 'newcity'
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

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

@pytest.mark.django_db
def test_form_ignores_unspecified_profile_fields():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity',
        'is_student': True,
        'title': 'title'
    })
    user = f.save()
    assert not user.profile.is_student
    assert user.profile.title == ''

def test_connect_form_requires_usernames():
    form = forms.parent.ConnectForm(data={})
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'required'

@pytest.mark.django_db
def test_connect_form_validates_existance():
    form = forms.parent.ConnectForm(data={
        "usernames": "nope"
    })
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'nonexistant-user'

@pytest.mark.django_db
def test_connect_form_connects_to_usernames():
    parent = User(username="parent")
    parent_profile = models.Profile(is_parent=True)
    parent_profile.user = parent
    parent.save()
    parent_profile.user = parent
    parent_profile.save()

    child = User(username="child")
    child_profile = models.Profile(is_student=True, birthday=datetime.now())
    child_profile.user = child
    child.save()
    child_profile.user = child
    child_profile.save()

    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    assert form.is_valid()
    assert models.ParentConnection.objects.all().count() == 0
    form.save()
    assert models.ParentConnection.objects.all().count() == 1
    assert [profile.id for profile in parent.profile.child_profiles.all()] == [child.profile.id]
    assert len(form.saved) == 1
    assert type(form.saved[0][0]) == models.ParentConnection
    assert form.saved[0][1] == True
