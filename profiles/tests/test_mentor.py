import pytest
import mock
from django.utils.timezone import now
from profiles import forms, models
import profiles.factories
import challenges.factories
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_gets_ok(client):
    mentor = profiles.factories.MentorFactory(username="mentor", password="password")
    client.login(username='mentor', password='password')

    assert client.get('/home/').status_code == 200
    assert client.get('/profile-edit/').status_code == 200

    student = profiles.factories.StudentFactory(username="student", password="password", profile__source="source")
    started = now()
    challenges.factories.ProgressFactory(started=started, comment=True, student=student)

    assert client.get('/unclaimed_progresses/%d/%d/%d' % (started.year, started.month, started.day)).status_code == 200
    assert client.get('/unclaimed_progresses/?source=source').status_code == 200

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

@pytest.mark.django_db
def test_mentor_join_form_clean_username_illegal_characters():
    f = forms.mentor.MentorUserAndProfileForm(data={
        'username': 'me!'
    })
    assert 'username' in f.errors
    assert 'can only include' in f.errors['username'].as_text()

@pytest.mark.django_db
def test_mentor_join_from_source_sets_source_from_url(client):
    res = client.get('/join_as_mentor/whatever/')
    assert res.context['source'] == 'whatever'
    assert res.context['form'].initial['source'] == 'whatever'

@pytest.mark.django_db
def test_post_to_join_as_mentor_strips_source(client):
    res = client.post('/join_as_mentor/', {
        'mentor-email': 'email@example.org',
        'mentor-username': 'username',
        'mentor-password': 'password',
        'mentor-confirm_password': 'password',
        'mentor-city': 'city',
        'mentor-source': 'source'
    })
    assert not User.objects.get(username='username').profile.source

@pytest.mark.django_db
def test_post_to_join_as_mentor_with_source_adds_source(client):
    res = client.post('/join_as_mentor/source/', {
        'mentor-email': 'email@example.org',
        'mentor-username': 'username',
        'mentor-password': 'password',
        'mentor-confirm_password': 'password',
        'mentor-city': 'city'
    })
    assert User.objects.get(username='username').profile.source == 'source'
