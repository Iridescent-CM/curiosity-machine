import pytest
import mock
from . import mailer, signals
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date, timedelta
from profiles.models import Profile
from images.models import Image
from challenges.models import Stage
import profiles.factories
import challenges.factories
import cmcomments.factories

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

@pytest.mark.django_db
def test_deliver_email_returns_none_if_it_cant_determine_user_type():
    user = User.objects.create_user(username='user', email='user@example.com', password='password')
    assert mailer.deliver_email('key', user.profile) == None

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

def test_determine_user_type_mentor():
    user = User(email='foo@example.com')
    profile = Profile(is_mentor=True)
    profile.user = user
    assert mailer.determine_user_type(profile) == mailer.MENTOR

def test_determine_user_type_student():
    user = User(email='foo@example.com')
    profile = Profile(is_student=True, birthday=date(1900, 1, 1))
    profile.user = user
    assert mailer.determine_user_type(profile) == mailer.STUDENT

def test_determine_user_type_underage():
    user = User(email='foo@example.com')
    profile = Profile(is_student=True, birthday=date.today())
    profile.user = user
    assert mailer.determine_user_type(profile) == mailer.UNDERAGE_STUDENT

def test_determine_user_type_educator():
    user = User(email='foo@example.com')
    profile = Profile(is_educator=True)
    profile.user = user
    assert mailer.determine_user_type(profile) == mailer.EDUCATOR

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

def test_handler_student_posted_comment_no_mentor():
    student = profiles.factories.StudentFactory.build()
    progress = challenges.factories.ProgressFactory.build()
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student)

    with mock.patch('cmemails.signals.handlers.deliver_email') as deliver_email:
        signals.handlers.student_posted_comment(student, comment)
        assert len(deliver_email.mock_calls) == 0

def test_handler_student_posted_comment():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor)
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student)

    with mock.patch('cmemails.signals.handlers.deliver_email') as deliver_email:
        signals.handlers.student_posted_comment(student, comment)
        assert len(deliver_email.mock_calls) == 1
        assert deliver_email.call_args[0][0] == 'student_responded'

def test_handler_student_posted_reflect_comment_with_image():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor)
    image = Image()
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student, image=image, stage=Stage.reflect.value)

    with mock.patch('cmemails.signals.handlers.deliver_email') as deliver_email:
        signals.handlers.student_posted_comment(student, comment)
        assert len(deliver_email.mock_calls) == 1
        assert deliver_email.call_args[0][0] == 'student_completed'
