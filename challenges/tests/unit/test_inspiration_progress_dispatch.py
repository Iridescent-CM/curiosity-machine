import pytest

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from challenges.views import InspirationProgressDispatch, InspirationStudentProgress, InspirationUserProgress
from profiles.factories import StudentFactory, MentorFactory

pytestmark = pytest.mark.unit

def test_select_student_view():
    user = StudentFactory.build()
    assert InspirationProgressDispatch.select_view_class(user) == InspirationStudentProgress

def test_select_non_student_user_view():
    user = MentorFactory.build()
    assert InspirationProgressDispatch.select_view_class(user) == InspirationUserProgress

def test_anonymous_view_denied():
    user = AnonymousUser()
    with pytest.raises(PermissionDenied):
        InspirationProgressDispatch.select_view_class(user)
    