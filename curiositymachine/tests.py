import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from profiles.models import Profile
from .middleware import UnderageStudentSandboxMiddleware, UnapprovedMentorSandboxMiddleware
from .views import root_redirect
from challenges.models import Progress, Challenge
from .helpers import random_string

def test_underage_student_middleware_redirects_request(rf):
    user = User()
    profile = Profile(user=user, is_student=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_request(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:underage_student')

def test_underage_student_middleware_skips_approved_profiles(rf):
    user = User()
    profile = Profile(user=user, approved=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_underage_student_middleware_skips_mentors(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_underage_student_middleware_skips_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user)
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_underage_student_middleware_skips_unauthenticated_user(rf):
    user = AnonymousUser()
    middleware = UnderageStudentSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_unapproved_mentor_middleware_redirects(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    response = middleware.process_request(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:home')

def test_unapproved_mentor_middleware_skips_approved(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True, approved=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_unapproved_mentor_middleware_skips_training_paths(rf):
    user = User()
    profile = Profile(user=user, is_mentor=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/training/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_unapproved_mentor_middleware_skips_non_mentor(rf):
    user = User()
    profile = Profile(user=user, is_mentor=False)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_unapproved_mentor_middleware_skips_staff(rf):
    user = User(is_staff=True)
    profile = Profile(user=user, is_mentor=True)
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_unapproved_mentor_middleware_skips_unauthenticated(rf):
    user = AnonymousUser()
    middleware = UnapprovedMentorSandboxMiddleware()
    request = rf.get('/some/path')
    request.user = user
    assert not middleware.process_request(request)

def test_root_redirect_redirects_student_without_progress_to_challenges(rf):
    user = User()
    profile = Profile(user=user, is_student=True)
    request = rf.get('/some/path')
    request.user = user
    response = root_redirect(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('challenges:challenges')

@pytest.mark.django_db
def test_root_redirect_redirects_student_with_progress_to_home(rf):
    user = User.objects.create(username='user', email='useremail')
    challenge = Challenge.objects.create(name='challenge')
    progress = Progress.objects.create(student=user, challenge=challenge)
    request = rf.get('/some/path')
    request.user = user
    response = root_redirect(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse('profiles:home')

def test_random_string():
    assert len(random_string()) == 5
    assert len(random_string(length=2)) == 2
    assert type(random_string()) is str
