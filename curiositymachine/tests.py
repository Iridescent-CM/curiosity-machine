import pytest
import mock
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from profiles.models import Profile
from .middleware import UnderageStudentSandboxMiddleware, UnapprovedMentorSandboxMiddleware, LoginRequiredMiddleware, LoginRequired
from .views import root
from .views.generic import UserJoinView
from challenges.models import Progress, Challenge, Example
from .helpers import random_string
from curiositymachine import decorators
from django.core.exceptions import PermissionDenied
from django.conf import settings
from . import signals
import challenges.factories
import profiles.factories

def force_true(*args, **kwargs):
    return True

def force_false(*args, **kwargs):
    return False

def test_underage_student_middleware_redirects_request(rf):
    user = User()
    profile = Profile(user=user, is_student=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_view(request, mock.MagicMock(), None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:underage_student')

def test_underage_student_middleware_skips_approved_profiles(rf):
    user = User()
    profile = Profile(user=user, approved=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_skips_mentors(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_underage_student_middleware_skips_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user)
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
    user = User()
    profile = Profile(user=user, is_student=True)
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
    user = User()
    profile = Profile(user=user, is_mentor=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_view(request, mock.MagicMock(), None, None)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:home')

def test_unapproved_mentor_middleware_skips_approved(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True, approved=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_unapproved_mentor_middleware_skips_whitelisted(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
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
    user = User()
    profile = Profile(user=user, is_mentor=False)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_view(request, mock.MagicMock(), None, None)

def test_unapproved_mentor_middleware_skips_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user, is_mentor=True)
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
    assert not middleware.process_exception(request, Http404())

    response = middleware.process_exception(request, LoginRequired())
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('login') + '?next=/some/path'

def test_root_redirects_student_without_progress_to_challenges(rf):
    user = User()
    profile = Profile(user=user, is_student=True)
    request = rf.get('/some/path')
    request.user = user
    response = root(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('challenges:challenges')

@pytest.mark.django_db
def test_root_redirects_student_with_progress_to_home(rf):
    user = User.objects.create(username='user', email='useremail')
    challenge = Challenge.objects.create(name='challenge')
    progress = Progress.objects.create(student=user, challenge=challenge)
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
    user = User()
    profile = Profile(user=user, is_student=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_mentor_only_calls_view_for_mentor(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.mentor_only(view)
    response = wrapped(request)
    assert view.called

def test_mentor_only_calls_view_for_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user)
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
    user = User()
    profile = Profile(user=user)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_student_only_calls_view_for_student(rf):
    user = User()
    profile = Profile(user=user, is_student=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.student_only(view)
    response = wrapped(request)
    assert view.called

def test_student_only_calls_view_for_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user)
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
    user = User()
    profile = Profile(user=user)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    with pytest.raises(PermissionDenied):
        response = wrapped(request)

def test_educator_only_calls_view_for_educator(rf):
    user = User()
    profile = Profile(user=user, is_educator=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.educator_only(view)
    response = wrapped(request)
    assert view.called

def test_educator_only_calls_view_for_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user)
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
    mentor = User()
    profile = Profile(user=mentor, is_mentor=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = mentor
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, 1, 'student')
    assert view.called

def test_challenge_access_decorator_allows_named_user(rf):
    user = User(username='named')
    profile = Profile(user=user)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, 1, 'named')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.users_share_any_group', force_true)
def test_challenge_access_decorator_allows_connected_group_owners(rf):
    user = User()
    profile = Profile(user=user)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, 1, 'student')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.users_share_any_group', force_false)
@mock.patch('profiles.models.Profile.is_parent_of', force_true)
def test_challenge_access_decorator_allows_connected_parent(rf):
    user = User()
    profile = Profile(user=user)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, 1, 'student')
    assert view.called

@mock.patch('curiositymachine.decorators.Membership.users_share_any_group', force_false)
@mock.patch('profiles.models.Profile.is_parent_of', force_false)
def test_challenge_access_decorator_redirects_other(rf):
    user = User(username='other')
    profile = Profile(user=user, is_student=True)
    view = mock.MagicMock()
    request = rf.get('/some/path')
    request.user = user
    wrapped = decorators.current_user_or_approved_viewer(view)
    response = wrapped(request, 1, 'named')
    assert not view.called
    assert response.status_code == 302

def test_user_join_view_redirects_logged_in_user(rf):
    request = rf.get('/whatever')
    user = User()
    profile = Profile(user=user)
    request.user = user
    view = UserJoinView.as_view(logged_in_redirect='/redirect')
    assert type(view(request)) == HttpResponseRedirect
    assert view(request).url == '/redirect'

def test_user_join_view_sets_source_in_initial_form_data(rf):
    request = rf.get('/whatever')
    request.user = AnonymousUser()

    m = mock.MagicMock()
    view = UserJoinView.as_view(form_class=m)
    view(request, source='source')

    args = m.call_args
    assert 'initial' in args[1]
    assert 'source' in args[1]['initial']
    assert args[1]['initial']['source'] == 'source'

def test_user_join_view_sets_source_in_form_data_from_url(rf):
    request = rf.post('/whatever', {'source': None})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def form_valid(self, form):
            pass

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m)
    view(request, source='source')

    args = m.call_args
    assert 'data' in args[1]
    assert 'source' in args[1]['data']
    assert args[1]['data']['source'] == 'source'

def test_user_join_view_strips_source_if_not_in_url(rf):
    request = rf.post('/whatever', {'source': 'source'})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def form_valid(self, form):
            pass

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m)
    view(request)

    args = m.call_args
    assert 'data' in args[1]
    assert 'source' not in args[1]['data']

def test_user_join_view_templates(rf):
    request = rf.get('/whatever')
    request.user = AnonymousUser()

    m = mock.MagicMock()
    view = UserJoinView.as_view(form_class=m, prefix='usertype')

    response = view(request)
    assert response.template_name == ['profiles/usertype/join.html']

    response = view(request, source='somesource')
    assert response.template_name == ['profiles/sources/somesource/usertype/join.html', 'profiles/usertype/join.html']

def test_user_join_view_redirects_to_success_url(rf):
    request = rf.post('/whatever', {})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def create_user(self, form):
            return mock.MagicMock()

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m, prefix='usertype', success_url='/success')

    response = view(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/success'

def test_user_join_view_redirects_to_welcome_url_from_form(rf):
    request = rf.post('/join/thisone/', {'welcome': 'true'})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def create_user(self, form):
            return mock.MagicMock()

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m, success_url='/success')

    response = view(request, source='thisone')
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/welcome/thisone'

@pytest.mark.django_db
def test_signal_student_started_first_project():
    handler = mock.MagicMock()
    signals.started_first_project.connect(handler)

    user = User.objects.create(username='user', email='useremail')
    challenge = Challenge.objects.create(name='challenge')
    first_progress = Progress.objects.create(student=user, challenge=challenge)

    challenge2 = Challenge.objects.create(name='challenge2')
    second_progress = Progress.objects.create(student=user, challenge=challenge2)

    handler.assert_called_once_with(signal=signals.started_first_project, progress=first_progress, sender=user)

@pytest.mark.django_db
def test_signal_mentor_approved_project_for_gallery():
    handler = mock.MagicMock()
    signals.approved_project_for_gallery.connect(handler)

    user = User.objects.create(username='user', email='useremail')
    user2 = User.objects.create(username='user2', email='useremail2')
    user2.profile.is_mentor=True
    challenge = Challenge.objects.create(name='challenge')
    progress = Progress.objects.create(student=user, challenge=challenge, mentor=user2)
    example = Example.objects.create(challenge=challenge, progress=progress)

    handler.assert_called_once_with(signal=signals.approved_project_for_gallery, sender=user2, example=example)

@pytest.mark.django_db
def test_signal_student_posted_comment():
    handler = mock.MagicMock()
    signals.posted_comment.connect(handler)

    progress = challenges.factories.ProgressFactory()
    comment = progress.comments.create(user=progress.student, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.posted_comment, sender=progress.student, comment=comment)

@pytest.mark.django_db
def test_signal_mentor_posted_comment():
    handler = mock.MagicMock()
    signals.posted_comment.connect(handler)

    mentor = profiles.factories.MentorFactory()
    progress = challenges.factories.ProgressFactory(mentor=mentor)
    comment = progress.comments.create(user=progress.mentor, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.posted_comment, sender=progress.mentor, comment=comment)

@pytest.mark.django_db
def test_signal_approved_project_for_reflection():
    handler = mock.MagicMock()
    signal = signals.approved_project_for_reflection
    signal.connect(handler)

    progress = challenges.factories.ProgressFactory()
    mentor = profiles.factories.MentorFactory()
    progress.approve(approver=mentor)

    handler.assert_called_once_with(signal=signal, sender=mentor, progress=progress)
