import mock
import pytest
from challenges.factories import *
from challenges.models import Stage
from cmcomments.factories import *
from datetime import date, timedelta
from django.utils.timezone import now
from educators.factories import *
from images.models import Image
from mentors.factories import *
from parents.factories import *
from profiles.factories import *
from profiles.models import UserRole
from students.factories import *
from . import signals
from .mailchimp import subscribe
from .mandrill import send_template

@pytest.fixture
def student():
    return StudentFactory(username='student', email='student@example.com', password='password')

def test_send_welcome_email_skips_excluded_user_types():
    mentor = MentorFactory.build()
    none = UserFactory.build()

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_welcome_email(mentor)
        signals.handlers.send_welcome_email(none)
        assert not send.called

def test_send_welcome_email_differentiates_user_categories():
    educator = EducatorFactory.build()
    parent = ParentFactory.build()

    with mock.patch('cmemails.signals.handlers.send') as send:
        signals.handlers.send_welcome_email(educator)
        assert send.call_args[1]['template_name'] == 'educator-welcome'
        signals.handlers.send_welcome_email(parent)
        assert send.call_args[1]['template_name'] == 'parent-welcome'

def test_send_template_handles_single_recipient():
    student = StudentFactory.build()

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
    students = StudentFactory.build_batch(2)

    with mock.patch('mandrill.Mandrill') as mandrill:
        send_template(template_name='foo', to=students)
        kwargs = mandrill().messages.send_template.call_args[1]
        assert ('message' in kwargs and len(kwargs['message']['to']) == 2)

def test_send_template_handles_single_cc():
    student = StudentFactory.build()

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
    student = StudentFactory.build()

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
    student = StudentFactory.build(email=None)
    student2 = StudentFactory.build()
    with mock.patch('mandrill.Mandrill') as mandrill:
        mandrill().messages.send_template = mock.Mock(return_value=[])

        send_template(template_name='foo', to=student)
        assert len(mandrill().messages.send_template.mock_calls) == 0
        send_template(template_name='foo', to=student, cc="email@example.com")
        assert len(mandrill().messages.send_template.mock_calls) == 0
        send_template(template_name='foo', to=[student, student2])
        assert len(mandrill().messages.send_template.mock_calls) == 1

def test_send_template_with_merge_vars():
    student = StudentFactory.build()
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
    student = StudentFactory.build()
    with mock.patch('cmemails.mailchimp.requests') as requests:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_API_KEY = None
            subscribe(student)

def test_mailchimp_subscribe_does_nothing_without_list_id_for_user_type():
    student = StudentFactory.build()
    with mock.patch('cmemails.mailchimp.requests') as requests:
        with mock.patch('cmemails.mailchimp.settings') as settings:
            settings.MAILCHIMP_LIST_IDS = {}
            subscribe(student)
            assert len(requests.put.mock_calls) == 0

def test_mailchimp_subscribe_does_nothing_without_email():
    student = StudentFactory.build(email='')
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
    student = StudentFactory.build()
    mentor = MentorFactory.build()
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
