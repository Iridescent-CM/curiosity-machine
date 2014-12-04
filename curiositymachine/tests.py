import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from profiles.models import Profile
from .middleware import UnderageStudentSandboxMiddleware, UnapprovedMentorSandboxMiddleware

def test_underage_student_middleware_redirects_request(rf):
    user = User()
    profile = Profile(user=user)
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
