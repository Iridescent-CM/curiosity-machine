import pytest
import mock
from . import mailer
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date, timedelta
from profiles.models import Profile

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.birthday = now() - timedelta(days=(365 * 16))
    student.profile.save()
    return student

@pytest.mark.django_db
def test_override_subject(student):
	assert mailer.deliver_email('welcome', student.profile) == None
	assert mailer.deliver_email('welcome', student.profile, subject='test') == None

def test_deliver_email_returns_none_if_it_cant_determine_user_type():
    profile = Profile()
    assert mailer.deliver_email('key', profile) == None

def test_deliver_email_looks_up_config_and_calls_email_if_it_can_determine_user_type():
    user = User(email='foo@example.com')
    profile = Profile(is_mentor=True)
    profile.user = user
    config = {
        'mentor_some_key': {
            'subject': 'some subject',
            'template':'template.html'
        }
    }
    mailer.email = mock.MagicMock(return_value=None)
    with mock.patch.dict(mailer.email_info, config):
        mailer.deliver_email('some_key', profile)
        assert mailer.email.called
        positional = mailer.email.call_args[0]
        assert positional[0] == [user.email]
        assert positional[1] == 'some subject'
        assert 'profile' in positional[2]
        assert positional[2]['profile'] == profile
        assert positional[3] == 'template.html'

def test_deliver_email_can_override_subject_from_config():
    user = User(email='foo@example.com')
    profile = Profile(is_mentor=True)
    profile.user = user
    config = {
        'mentor_some_key': {
            'subject': 'some subject',
            'template':'template.html'
        }
    }
    mailer.email = mock.MagicMock(return_value=None)
    with mock.patch.dict(mailer.email_info, config):
        mailer.deliver_email('some_key', profile, subject="new subject")
        assert mailer.email.called
        positional = mailer.email.call_args[0]
        assert positional[1] == 'new subject'

def test_deliver_email_named_arguments_become_email_context():
    user = User(email='foo@example.com')
    profile = Profile(is_mentor=True)
    profile.user = user
    config = {
        'mentor_some_key': {
            'subject': 'some subject',
            'template':'template.html'
        }
    }
    mailer.email = mock.MagicMock(return_value=None)
    with mock.patch.dict(mailer.email_info, config):
        mailer.deliver_email('some_key', profile, progress=1, student=2, mentor=3, stage=4, task=5)
        assert mailer.email.called
        positional = mailer.email.call_args[0]
        assert positional[2] == {
            'progress': 1,
            'student': 2,
            'mentor': 3,
            'stage': 4,
            'task': 5,
            'profile': profile
        }
