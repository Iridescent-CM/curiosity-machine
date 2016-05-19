import pytest
from django.contrib.auth.models import AnonymousUser
from challenges.views import InspirationPreviewDispatch, InspirationStudentPreview, InspirationUserPreview, InspirationAnonymousPreview
from profiles.factories import StudentFactory, MentorFactory

pytestmark = pytest.mark.unit

def test_select_student_view():
    user = StudentFactory.build()
    assert InspirationPreviewDispatch.select_view_class(user) == InspirationStudentPreview

def test_select_non_student_user_view():
    user = MentorFactory.build()
    assert InspirationPreviewDispatch.select_view_class(user) == InspirationUserPreview

def test_select_anonymous_view():
    user = AnonymousUser()
    assert InspirationPreviewDispatch.select_view_class(user) == InspirationAnonymousPreview
    