import mock
import pytest
from challenges.factories import *
from challenges.models import Progress, Challenge, Example
from cmcomments.factories import *
from curiositymachine import decorators
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget, FilePickerImagePickWidget, FilePickerVideoPickWidget
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from educators.factories import *
from mentors.factories import *
from parents.factories import *
from profiles.factories import *
from profiles.models import Profile, UserRole
from pyquery import PyQuery as pq
from students.factories import *
from .. import signals
from ..helpers import random_string
from ..middleware import UnderageStudentSandboxMiddleware, UnapprovedMentorSandboxMiddleware, LoginRequiredMiddleware, LoginRequired
from ..views import root

User = get_user_model()

def force_true(*args, **kwargs):
    return True

def force_false(*args, **kwargs):
    return False

def test_underage_student_middleware_redirects_request(rf):
    user = StudentFactory.build(profile__underage=True, extra__approved=False)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_view(request, mock.MagicMock(), None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('students:underage')

def test_underage_student_middleware_skips_approved_profiles(rf):
    user = UserFactory.build(extra__approved=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_skips_mentors(rf):
    user = MentorFactory.build()
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_skips_staff(rf):
    user = UserFactory.build(is_staff=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_skips_unauthenticated_user(rf):
    user = AnonymousUser()
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_allows_whitelisted_views(rf):
    user = StudentFactory.build(profile__underage=True, extra__approved=False)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user

    view = decorators.whitelist('public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

    view = decorators.whitelist('maybe_public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

    view = decorators.whitelist('underage')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

def test_unapproved_mentor_middleware_redirects(rf):
    user = MentorFactory.build(extra__approved=False)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_view(request, mock.MagicMock(), None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:home')

def test_unapproved_mentor_middleware_skips_approved(rf):
    user = MentorFactory.build(extra__approved=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_unapproved_mentor_middleware_skips_whitelisted(rf):
    user = MentorFactory.build(extra__approved=False)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user

    view = decorators.whitelist('public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

    view = decorators.whitelist('maybe_public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

    view = decorators.whitelist('unapproved_mentors')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

def test_unapproved_mentor_middleware_skips_non_mentor(rf):
    user = UserFactory.build()
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_unapproved_mentor_middleware_skips_staff(rf):
    user = MentorFactory.build(is_staff=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_unapproved_mentor_middleware_skips_unauthenticated(rf):
    user = AnonymousUser()
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_login_required_middleware_skips_whitelisted(rf):
    user = AnonymousUser()
    middleware = LoginRequiredMiddleware()
    request = rf.get('/some/path')
    request.user = user
    view = decorators.whitelist('public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

    view = decorators.whitelist('maybe_public')(mock.MagicMock())
    assert not middleware.process_view(request, view, None, None)

def test_login_required_middleware_redirects_if_not_public(rf):
    user = AnonymousUser()
    middleware = LoginRequiredMiddleware()
    request = rf.get('/some/path')
    request.user = user
    setattr(request, '_messages', mock.MagicMock())
    view = mock.MagicMock()

    response = middleware.process_view(request, view, None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('login') + '?next=/some/path'

    view = decorators.whitelist('something_not_public')(mock.MagicMock)
    response = middleware.process_view(request, view, None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('login') + '?next=/some/path'

def test_login_required_middleware_redirects_login_required_exceptions(rf):
    middleware = LoginRequiredMiddleware()
    request = rf.get('/some/path')
    setattr(request, '_messages', mock.MagicMock())
    assert not middleware.process_exception(request, Http404())

    response = middleware.process_exception(request, LoginRequired())
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('login') + '?next=/some/path'

def test_root_redirects_student_without_progress_to_challenges(rf):
    user = StudentFactory.build()
    request = rf.get('/some/path')
    request.user = user
    response = root(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('challenges:challenges')

@pytest.mark.django_db
def test_root_redirects_student_with_progress_to_home(rf):
    user = StudentFactory()
    progress = ProgressFactory(student=user)
    request = rf.get('/some/path')
    request.user = user
    response = root(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:home')

def test_random_string():
    assert len(random_string()) == 5
    assert len(random_string(length=2)) == 2
    assert type(random_string()) is str

def test_mentor_only_denies_view_for_anonymous_user(rf):
    user = AnonymousUser()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_mentor_only_denies_view_for_non_mentor_or_staff(rf):
    user = StudentFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_mentor_only_calls_view_for_mentor(rf):
    user = MentorFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    response = wrapped(request)
    assert view.called

def test_mentor_only_calls_view_for_staff(rf):
    user = UserFactory.build(is_staff=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    response = wrapped(request)
    assert view.called

def test_student_only_denies_view_for_anonymous_user(rf):
    user = AnonymousUser()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_student_only_denies_view_for_non_student_or_staff(rf):
    user = UserFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_student_only_calls_view_for_student(rf):
    user = StudentFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    response = wrapped(request)
    assert view.called

def test_student_only_calls_view_for_staff(rf):
    user = UserFactory.build(is_staff=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    response = wrapped(request)
    assert view.called

def test_educator_only_denies_view_for_anonymous_user(rf):
    user = AnonymousUser()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_educator_only_denies_view_for_non_educator_or_staff(rf):
    user = UserFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_educator_only_calls_view_for_educator(rf):
    user = EducatorFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    response = wrapped(request)
    assert view.called

def test_educator_only_calls_view_for_staff(rf):
    user = UserFactory.build(is_staff=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    response = wrapped(request)
    assert view.called

def test_feature_flag_404s_if_flag_missing(rf):
    view = mock.MagicMock()
    request = rf.get('/some/path')
    wrapped = decorators.feature_flag('test_flag')(view)
    with pytest.raises(Http404):
        response = wrapped(request)

def test_feature_flag_404s_if_flag_false(rf):
    view = mock.MagicMock()
    request = rf.get('/some/path')
    wrapped = decorators.feature_flag('test_flag')(view)
    with mock.patch.dict(settings.FEATURE_FLAGS, {'test_flag': False}):
        with pytest.raises(Http404):
            response = wrapped(request)

def test_feature_flag_calls_view_if_flag_true(rf):
    view = mock.MagicMock()
    request = rf.get('/some/path')
    wrapped = decorators.feature_flag('test_flag')(view)
    with mock.patch.dict(settings.FEATURE_FLAGS, {'test_flag': True}):
        response = wrapped(request)
        assert view.called

def test_challenge_access_decorator_allows_any_mentor(rf):
    mentor = MentorFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = mentor
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='student')
    assert view.called

def test_challenge_access_decorator_allows_named_user(rf):
    user = UserFactory.build(username='named')
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='named')
    assert view.called

@pytest.mark.django_db
def test_challenge_access_decorator_allows_connected_parent(rf):
    parent = ParentFactory()
    child = StudentFactory(username="student")
    ParentConnectionFactory(
        parent_profile=parent.parentprofile,
        child_profile=child.studentprofile,
        active=True
    )
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = parent
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='student')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.share_membership', force_true)
@mock.patch('profiles.models.Profile.is_parent_of', force_false)
def test_challenge_access_decorator_allows_membership_parent(rf):
    user = UserFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='student')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.share_membership', force_true)
@mock.patch('profiles.models.Profile.is_parent_of', force_false)
def test_challenge_access_decorator_allows_membership_educator(rf):
    user = UserFactory.build()
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='student')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.share_membership', force_false)
@mock.patch('profiles.models.Profile.is_parent_of', force_false)
def test_challenge_access_decorator_redirects_other(rf):
    user = StudentFactory.build(username='other')
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, challenge_id=1, username='named')
    assert not view.called
    assert response.status_code == 302

@pytest.mark.django_db
def test_signal_student_started_first_project():
    handler = mock.MagicMock()
    signals.started_first_project.connect(handler)

    user = User.objects.create(username='user', email='useremail')
    challenge = Challenge.objects.create(name='challenge')
    first_progress = Progress.objects.create(student=user, challenge=challenge)

    assert not handler.called

    first_progress.comments.create(user=user, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.started_first_project, progress=first_progress, sender=user)
    handler.reset_mock()

    challenge2 = Challenge.objects.create(name='challenge2')
    second_progress = Progress.objects.create(student=user, challenge=challenge2)
    second_progress.comments.create(user=user, text="comment", stage=1)

    assert not handler.called


@pytest.mark.django_db
def test_signal_student_posted_comment():
    handler = mock.MagicMock()
    signals.posted_comment.connect(handler)

    progress = ProgressFactory()
    comment = progress.comments.create(user=progress.student, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.posted_comment, sender=progress.student, comment=comment)

@pytest.mark.django_db
def test_signal_mentor_posted_comment():
    handler = mock.MagicMock()
    signals.posted_comment.connect(handler)

    mentor = MentorFactory()
    progress = ProgressFactory(mentor=mentor)
    comment = progress.comments.create(user=progress.mentor, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.posted_comment, sender=progress.mentor, comment=comment)

@pytest.mark.django_db
def test_signal_progress_considered_complete():
    handler = mock.MagicMock()
    signal = signals.progress_considered_complete
    signal.connect(handler)

    handler2 = mock.MagicMock()
    signals.posted_comment.connect(handler2)

    progress = ProgressFactory()
    mentor = MentorFactory()
    first_reflect_post = ReflectionCommentFactory(challenge_progress=progress, user=progress.student)

    handler.assert_called_once_with(signal=signal, sender=progress.student, progress=progress)
    handler2.assert_not_called()

@pytest.mark.django_db
def test_signal_created_account():
    handler = mock.MagicMock()
    signal = signals.created_account
    signal.connect(handler)

    user = User.objects.create(username='user', email='email')

    handler.assert_called_once_with(signal=signal, sender=user)

@pytest.mark.django_db
def test_signal_inspiration_gallery_submission_created():
    handler = mock.MagicMock()
    signal = signals.inspiration_gallery_submission_created
    signal.connect(handler)

    example = ExampleFactory()

    handler.assert_called_once_with(signal=signal, sender=example.progress.student, example=example)

@pytest.mark.django_db
def test_signal_inspiration_gallery_submissions_rejected():
    handler = mock.MagicMock()
    signal = signals.inspiration_gallery_submissions_rejected
    signal.connect(handler)

    example = ExampleFactory()
    user = UserFactory()
    qs = Example.objects.all()
    qs.reject(user=user)

    handler.assert_called_once_with(signal=signal, sender=user, queryset=qs)

@pytest.mark.django_db
def test_signal_inspiration_gallery_submissions_approved():
    handler = mock.MagicMock()
    signal = signals.inspiration_gallery_submissions_approved
    signal.connect(handler)

    example = ExampleFactory()
    user = UserFactory()
    qs = Example.objects.all()
    qs.approve(user=user)

    handler.assert_called_once_with(signal=signal, sender=user, queryset=qs)

def test_mediaurlfield_value_is_dictionary():
    class MyForm(forms.Form):
        mediaURL = MediaURLField()

    val = {
        "url": "http://s3.amazonaws.com/devcuriositymachine/images/eb76a9bbae527a3d9ca2faf12baa0216",
        "mimetype": "img/png"
    }

    form = MyForm(initial={ "mediaURL": val })
    assert form['mediaURL'].value() == val

    form = MyForm(data={
        "mediaURL_url": val['url'],
        "mediaURL_mimetype": val['mimetype']
    })
    assert form.is_valid()
    assert form.cleaned_data['mediaURL'] == val

def test_mediaurlfield_sets_default_mimetypes_on_widget():
    class MyForm(forms.Form):
        mediaURL = MediaURLField()

    form = MyForm()
    d = pq(str(form['mediaURL']))
    assert d('button').attr('data-fp-mimetypes') == '*/*'

def test_mediaurlfield_sets_specified_mimetypes_on_widget():
    class MyForm(forms.Form):
        mediaURL = MediaURLField(mimetypes='image/*,video/*')

    form = MyForm()
    d = pq(str(form['mediaURL']))
    assert d('button').attr('data-fp-mimetypes') == 'image/*,video/*'

def test_filepickerpickwidget_sets_basic_data_attrs_and_class():
    widget = FilePickerPickWidget()
    d = pq(widget.render('name', 'value'))
    assert d('button').attr('data-fp-apikey')
    assert 'pickwidget-button' in d('button').attr('class').split(' ')

def test_filepickerpickwidget_sets_preview_data_attr():
    widget = FilePickerPickWidget(preview=True)
    d = pq(widget.render('name', 'value'))
    assert d('button').attr('data-show-preview')

def test_filepickerimagepickwidget_sets_mimetype():
    widget = FilePickerImagePickWidget()
    d = pq(widget.render('name', 'value'))
    assert d('button').attr('data-fp-mimetypes') == 'image/*'

def test_filepickerimagepickwidget_returns_url_only():
    widget = FilePickerImagePickWidget()
    assert widget.value_from_datadict({
        "fieldname_url": "http://s3.amazonaws.com/devcuriositymachine/images/eb76a9bbae527a3d9ca2faf12baa0216",
        "fieldname_mimetype": "img/png"
    }, None, "fieldname") == "http://s3.amazonaws.com/devcuriositymachine/images/eb76a9bbae527a3d9ca2faf12baa0216"

def test_filepickervideopickwidget_sets_mimetype():
    widget = FilePickerVideoPickWidget()
    d = pq(widget.render('name', 'value'))
    assert d('button').attr('data-fp-mimetypes') == 'video/*'

def test_filepickervideopickwidget_returns_url_only():
    widget = FilePickerVideoPickWidget()
    assert widget.value_from_datadict({
        "fieldname_url": "http://s3.amazonaws.com/devcuriositymachine/images/eb76a9bbae527a3d9ca2faf12baa0216",
        "fieldname_mimetype": "video/mp4"
    }, None, "fieldname") == "http://s3.amazonaws.com/devcuriositymachine/images/eb76a9bbae527a3d9ca2faf12baa0216"

## Test fixture management command
#  TODO: move this to its own file
from django.core.management import call_command
from django.utils.six import StringIO
from curiositymachine.management.commands.fixtures import Command
@pytest.mark.parametrize("fixture", Command().get_available())
@pytest.mark.django_db
def test_fixtures_command(fixture):
    out = StringIO()
    call_command('fixtures', fixture, stdout=out)
    assert 'OK' in out.getvalue()
