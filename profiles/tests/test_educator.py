import pytest
from profiles import forms, models
from images.models import Image
from django.contrib.auth.models import User

def test_educator_user_creation_form_fields():
    f = forms.educator.UserCreationForm({})

    assert f.fields['username'].required
    assert f.fields['email'].required
    assert f.fields['password'].required
    assert f.fields['confirm_password'].required

    assert not f.fields['first_name'].required
    assert not f.fields['last_name'].required

def test_educator_user_creation_validates_password_length():
    errors = forms.educator.UserCreationForm({
        'password': 'abc'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert "must be at least" in str(errors['password'])

def test_educator_user_creation_checks_password_confirmation():
    errors = forms.educator.UserCreationForm({
        'password': 'abc123',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' not in errors.keys()
    assert 'confirm_password' not in errors.keys()
    assert '__all__' not in errors.keys()

    errors = forms.educator.UserCreationForm({
        'password': 'xxxxxx',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

@pytest.mark.django_db
def test_educator_user_creation_checks_username_uniqueness():
    User.objects.create(
        username='newuser',
        email='newuser@example.com',
        password='mypassword'
    )
    f = forms.educator.UserCreationForm({
        'username': 'newuser'
    })
    assert 'username' in f.errors.as_data().keys()
    assert "already exists" in str(f.errors['username'])

@pytest.mark.django_db
def test_educator_user_creation_saves():
    f = forms.educator.UserCreationForm({
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'mypassword',
        'confirm_password': 'mypassword'
    })
    f.save()
    assert User.objects.filter(username='newuser').count() == 1

def test_educator_user_change_form_fields():
    f = forms.educator.UserChangeForm({})

    assert not f.fields['email'].required
    assert not f.fields['password'].required
    assert not f.fields['confirm_password'].required
    assert not f.fields['first_name'].required
    assert not f.fields['last_name'].required

def test_educator_user_change_validates_password_length():
    errors = forms.educator.UserChangeForm({
        'password': 'abc'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert "must be at least" in str(errors['password'])

def test_educator_user_change_checks_password_confirmation():
    errors = forms.educator.UserChangeForm({
        'password': 'abc123',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' not in errors.keys()
    assert 'confirm_password' not in errors.keys()
    assert '__all__' not in errors.keys()

    errors = forms.educator.UserChangeForm({
        'password': 'xxxxxx',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

    errors = forms.educator.UserChangeForm({
        'password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

    errors = forms.educator.UserChangeForm({
        'confirm_password': 'abc123'
    }).errors.as_data()
    # Note: not sure how to detect 'password' missing from cleaned_data because
    # it wasn't provided vs. it failed validation. Could set "Please provide valid
    # password" as error on 'confirm_password' when we have it but no 'password'
    # in clean()
    assert 'password' not in errors.keys()
    assert 'confirm_password' not in errors.keys()
    assert '__all__' not in errors.keys()

@pytest.mark.django_db
def test_educator_user_change_saves():
    user = User.objects.create(
        username='newuser',
        email='newuser@example.com',
        password='mypassword'
    )
    f = forms.educator.UserChangeForm({
        'email': 'newemail@example.com'  
    }, instance = user)
    profile = f.save()
    assert User.objects.count() == 1
    assert User.objects.filter(email='newemail@example.com').count() == 1

def test_educator_profile_change_form_fields():
    f = forms.educator.ProfileChangeForm({})

    assert not f.fields['image_url'].required

def test_educator_profile_change_form_sets_permissions():
    f = forms.educator.ProfileChangeForm({})
    f.is_valid()

    assert f.cleaned_data['is_educator'] == True
    assert 'is_mentor' not in f.cleaned_data.keys()
    assert 'is_student' not in  f.cleaned_data.keys()

def test_educator_profile_change_form_ignores_permission_overrides():
    f = forms.educator.ProfileChangeForm({
        'is_educator': False,
        'is_mentor': True,
        'is_student': True
    })
    f.is_valid()

    assert f.cleaned_data['is_educator'] == True
    assert 'is_mentor' not in f.cleaned_data.keys()
    assert 'is_student' not in  f.cleaned_data.keys()

@pytest.mark.django_db
def test_educator_profile_change_form_saves():
    # Note: creating a User creates an empty profile, which we then update
    # even for a new user
    user = User.objects.create(
        username='newuser',
        email='newuser@example.com',
        password='mypassword'
    )
    f = forms.educator.ProfileChangeForm({
        'image_url': "http://example.com/"
    }, instance = user.profile)
    p = f.save()
    assert models.Profile.objects.count() == 1
    assert User.objects.count() == 1
    assert User.objects.all()[0].profile == p

def test_educator_profile_change_form_creates_image_from_image_url():
    f = forms.educator.ProfileChangeForm({
        'image_url': "http://example.com/"
    })
    p = f.save(commit=False)
    assert type(p.image) == Image
    assert p.image.source_url == 'http://example.com/'
