import pytest
import mock
from . import signals
from .mandrill import send_template
from .mailchimp import subscribe
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import date, timedelta
from profiles.models import Profile, UserRole
from images.models import Image
from challenges.models import Stage
import profiles.factories
import challenges.factories
import cmcomments.factories

User = get_user_model()

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.role = UserRole.student.value
    student.profile.birthday = now() - timedelta(days=(365 * 16))
    student.profile.save()
    return student

def test_send_mentor_progress_update_notice_no_mentor():
    student = profiles.factories.StudentFactory.build()
    progress = challenges.factories.ProgressFactory.build()
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_mentor_progress_update_notice(comment.user, comment)
        assert len(send.mock_calls) == 0

def test_send_mentor_progress_update_notice_on_mentor_comment():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor)
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=mentor)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_mentor_progress_update_notice(comment.user, comment)
        assert len(send.mock_calls) == 0

def test_send_mentor_progress_update_notice():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor, challenge__id=5)
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student, stage=Stage.inspiration.value)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_mentor_progress_update_notice(comment.user, comment)
        assert len(send.mock_calls) == 1
        assert send.call_args[1]['template_name'] == 'mentor-student-responded-to-feedback'
        assert "studentname" in send.call_args[1]['merge_vars']
        assert "progress_url" in send.call_args[1]['merge_vars']
        assert "://" not in send.call_args[1]['merge_vars']['progress_url'] # Mailchimp's WYSIWYG insists on adding the protocol

def test_send_student_mentor_reponse_notice_on_student_comment():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor)
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=student)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_student_mentor_response_notice(comment.user, comment)
        assert len(send.mock_calls) == 0

def test_send_student_mentor_response_notice():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(mentor=mentor, challenge__id=5)
    comment = cmcomments.factories.CommentFactory.build(challenge_progress=progress, user=mentor)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_student_mentor_response_notice(comment.user, comment)
        assert len(send.mock_calls) == 1
        assert send.call_args[1]['template_name'] == 'student-mentor-feedback'
        assert "studentname" in send.call_args[1]['merge_vars']
        assert "button_url" in send.call_args[1]['merge_vars']
        assert "://" not in send.call_args[1]['merge_vars']['button_url'] # Mailchimp's WYSIWYG insists on adding the protocol

def test_send_mentor_progress_completion_notice_no_mentor():
    student = profiles.factories.StudentFactory.build()
    progress = challenges.factories.ProgressFactory.build()

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_mentor_progress_completion_notice(student, progress)
        assert len(send.mock_calls) == 0

def test_send_mentor_progress_completion_notice():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    progress = challenges.factories.ProgressFactory.build(student=student, mentor=mentor, challenge__id=5)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_mentor_progress_completion_notice(student, progress)
        assert len(send.mock_calls) == 1
        assert send.call_args[1]['template_name'] == 'mentor-student-completed-project'
        assert "studentname" in send.call_args[1]['merge_vars']
        assert "progress_url" in send.call_args[1]['merge_vars']

def test_send_student_challenge_share_encouragement():
    student = profiles.factories.StudentFactory.build()
    progress = challenges.factories.ProgressFactory.build(student=student, challenge__id=5)

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_student_challenge_share_encouragement(student, progress)
        assert len(send.mock_calls) == 1
        assert send.call_args[1]['template_name'] == 'student-completed-project'
        assert "studentname" in send.call_args[1]['merge_vars']
        assert "challengename" in send.call_args[1]['merge_vars']
        assert "inspiration_url" in send.call_args[1]['merge_vars']

def test_send_welcome_email_skips_excluded_user_types():
    mentor = profiles.factories.MentorFactory.build()
    none = profiles.factories.UserFactory.build()

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_welcome_email(mentor)
        signals.handlers.send_welcome_email(none)
        assert not send.called

def test_send_welcome_email_differentiates_user_categories():
    student = profiles.factories.StudentFactory.build()
    underage = profiles.factories.StudentFactory.build(profile__underage=True)
    educator = profiles.factories.EducatorFactory.build()
    parent = profiles.factories.ParentFactory.build()

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_welcome_email(student)
        assert send.call_args[1]['template_name'] == 'student-welcome'
        signals.handlers.send_welcome_email(underage)
        assert send.call_args[1]['template_name'] == 'student-u13-welcome'
        signals.handlers.send_welcome_email(educator)
        assert send.call_args[1]['template_name'] == 'educator-welcome'
        signals.handlers.send_welcome_email(parent)
        assert send.call_args[1]['template_name'] == 'parent-welcome'

def test_send_template_handles_single_recipient():
    student = profiles.factories.StudentFactory.build()

    with mock.patch('mandrill.Mandrill') as mandrill:
        send_template(template_name='foo', to=student)
        kwargs = mandrill().messages.send_template.call_args[1]
        assert 'template_name' in kwargs and kwargs['template_name'] == 'foo'
        assert ('message' in kwargs and
            len(kwargs['message']['to']) == 1 and
            kwargs['message']['to'][0] == {
                "email": student.email,
                "name": student.username,
                "type": "to"
            })

def test_send_template_handles_multiple_recipients():
    students = profiles.factories.StudentFactory.build_batch(2)

    with mock.patch('mandrill.Mandrill') as mandrill:
        send_template(template_name='foo', to=students)
        kwargs = mandrill().messages.send_template.call_args[1]
        assert ('message' in kwargs and len(kwargs['message']['to']) == 2)

def test_send_template_handles_single_cc():
    student = profiles.factories.StudentFactory.build()

    with mock.patch('mandrill.Mandrill') as mandrill:
        send_template(template_name='foo', to=student, cc="someemail@example.com")
        kwargs = mandrill().messages.send_template.call_args[1]
        assert 'message' in kwargs
        assert len(kwargs['message']['to']) == 2
        assert {
            "email": "someemail@example.com",
            "type": "cc"
        } in kwargs['message']['to']

def test_send_template_handles_multiple_ccs():
    student = profiles.factories.StudentFactory.build()

    with mock.patch('mandrill.Mandrill') as mandrill:
        send_template(template_name='foo', to=student, cc=["someemail@example.com", "someotheremail@example.com"])
        kwargs = mandrill().messages.send_template.call_args[1]
        assert 'message' in kwargs
        assert len(kwargs['message']['to']) == 3
        assert {
            "email": "someemail@example.com",
            "type": "cc"
        } in kwargs['message']['to']
        assert {
            "email": "someotheremail@example.com",
            "type": "cc"
        } in kwargs['message']['to']

def test_send_template_skips_users_without_email():
    student = profiles.factories.StudentFactory.build(email=None)
    student2 = profiles.factories.StudentFactory.build()
    with mock.patch('mandrill.Mandrill') as mandrill:
        mandrill().messages.send_template = mock.Mock(return_value=[])

        send_template(template_name='foo', to=student)
        assert len(mandrill().messages.send_template.mock_calls) == 0
        send_template(template_name='foo', to=student, cc="email@example.com")
        assert len(mandrill().messages.send_template.mock_calls) == 0
        send_template(template_name='foo', to=[student, student2])
        print("YYYYYYYYYYYYYYYYYYYYYYYY", mandrill().messages.send_template.mock_calls)
        assert len(mandrill().messages.send_template.mock_calls) == 1

def test_send_template_with_merge_vars():
    student = profiles.factories.StudentFactory.build()
    with mock.patch('mandrill.Mandrill') as mandrill:
        mandrill().messages.send_template = mock.Mock(return_value=[])

        send_template(template_name="foo", to=student, merge_vars={"vars": "go here", "all": "of them"})
        assert len(mandrill().messages.send_template.mock_calls) == 1
        message = mandrill().messages.send_template.call_args[1]['message']
        expected = [
            {"name": "vars", "content": "go here"},
            {"name": "all", "content": "of them"}
        ]
        assert len(message["global_merge_vars"]) == len(expected)
        assert all(x in message["global_merge_vars"] for x in expected)

def test_mailchimp_subscribe_does_nothing_without_api_key():
    student = profiles.factories.StudentFactory.build()
    with mock.patch('cmemails.mailchimp.requests') as requests:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_API_KEY = None
            subscribe(student)

def test_mailchimp_subscribe_does_nothing_without_list_id_for_user_type():
    student = profiles.factories.StudentFactory.build()
    with mock.patch('cmemails.mailchimp.requests') as requests:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_LIST_IDS = {}
            subscribe(student)
            assert len(requests.put.mock_calls) == 0

def test_mailchimp_subscribe_does_nothing_without_email():
    student = profiles.factories.StudentFactory.build(email='')
    with mock.patch('cmemails.mailchimp.requests') as requests:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_DATA_CENTER = 'x'
            settings.MAILCHIMP_API_KEY = 'abc'
            settings.MAILCHIMP_LIST_IDS = {
                "student": 123,
            }
            subscribe(student)
            assert len(requests.put.mock_calls) == 0

def test_mailchimp_subscribe_subscribes_user():
    student = profiles.factories.StudentFactory.build()
    mentor = profiles.factories.MentorFactory.build()
    with mock.patch('cmemails.mailchimp._put') as put:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_DATA_CENTER = 'x'
            settings.MAILCHIMP_API_KEY = 'abc'
            settings.MAILCHIMP_LIST_IDS = {
                "student": 123,
                "mentor": 456
            }
            subscribe(student)
            assert len(put.mock_calls) > 0
            assert put.mock_calls[0].call_list()[0][1][0].startswith('https://x.api.mailchimp.com/3.0/lists/123/members/')

            put.reset_mock()
            subscribe(mentor)
            assert put.mock_calls[0].call_list()[0][1][0].startswith('https://x.api.mailchimp.com/3.0/lists/456/members/')
