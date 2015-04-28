import pytest
import mock
from django.conf import settings
from profiles import forms, models, views
from images.models import Image
from django.http import Http404
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

def test_educator_user_creation_validates_username():
    f = forms.educator.UserCreationForm({
        'username': 'user!'
    })
    assert 'username' in f.errors.as_data().keys()
    assert "can only include" in str(f.errors['username'])

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

    assert f.fields['city'].required
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
        'image_url': "http://example.com/",
        'city': 'some city'
    }, instance = user.profile)
    p = f.save()
    assert models.Profile.objects.count() == 1
    assert User.objects.count() == 1
    assert User.objects.all()[0].profile == p

def test_educator_profile_change_form_creates_image_from_image_url():
    f = forms.educator.ProfileChangeForm({
        'image_url': "http://example.com/",
        'city': "some city"
    })
    p = f.save(commit=False)
    assert type(p.image) == Image
    assert p.image.source_url == 'http://example.com/'

@pytest.mark.django_db
def test_join_sends_welcome_email(rf):
    with mock.patch.dict(settings.FEATURE_FLAGS, {'enable_educators': True}):
        with mock.patch('profiles.models.deliver_email') as deliver_email:
            request = rf.post('/join_as_educator', data={
                'user-username': 'user',
                'user-email': 'email@example.com',
                'user-password': '123123',
                'user-confirm_password': '123123',
                'profile-city': 'city'
            })
            request.session = mock.MagicMock()
            response = views.educator.join(request)
            assert deliver_email.called
            assert deliver_email.call_count == 1
            assert deliver_email.call_args[0][0] == "welcome"
            assert deliver_email.call_args[0][1].user.email == "email@example.com"

@pytest.mark.django_db
def test_join_with_feature_flag(rf):
    with mock.patch.dict(settings.FEATURE_FLAGS, {'enable_educators': True}):
        request = rf.post('/join_as_educator', data={
            'user-username': 'user',
            'user-email': 'email@example.com',
            'user-password': '123123',
            'user-confirm_password': '123123',
            'profile-city': 'city'
        })
        request.session = mock.MagicMock()
        response = views.educator.join(request)
        assert response.status_code == 302
        assert User.objects.filter(username='user').count() == 1

@pytest.mark.django_db
def test_join(rf):
    request = rf.post('/join_as_educator', data={
        'user-username': 'user',
        'user-email': 'email@example.com',
        'user-password': '123123',
        'user-confirm_password': '123123'
    })
    request.session = mock.MagicMock()
    with pytest.raises(Http404):
        views.educator.join(request)
