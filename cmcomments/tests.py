import pytest
from mock import MagicMock

from profiles.tests import student, mentor
from challenges.tests.fixtures import progress, challenge

from .models import Comment
from .factories import CommentFactory, ReflectionCommentFactory
from challenges.factories import ProgressFactory
from profiles.factories import StudentFactory, MentorFactory

from curiositymachine import signals

@pytest.fixture
def mentor_comment(mentor, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.mark.django_db
def test_unread_comment_count_for_mentors(mentor, student, mentor_comment):
    assert not mentor_comment.read
    assert mentor.profile.get_unread_comment_count() == 0
    assert student.profile.get_unread_comment_count() == 1

    mentor_comment.read = True
    mentor_comment.save()
    assert student.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_unread_comment_count_for_mentors(mentor, student, student_comment):
    assert not student_comment.read
    assert mentor.profile.get_unread_comment_count() == 1
    assert student.profile.get_unread_comment_count() == 0

    student_comment.read = True
    student_comment.save()
    assert mentor.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_is_first_reflect_post():
    student = StudentFactory()
    progress = ProgressFactory(student=student)
    assert not CommentFactory(challenge_progress=progress, user=student).is_first_reflect_post()
    assert ReflectionCommentFactory(challenge_progress=progress, user=student).is_first_reflect_post()
    assert not ReflectionCommentFactory(challenge_progress=progress, user=student).is_first_reflect_post()

@pytest.mark.django_db
def test_progress_considered_complete_sent_on_student_reflection():
    handler = MagicMock()
    signals.progress_considered_complete.connect(handler) 

    student = StudentFactory()
    progress = ProgressFactory(student=student)
    comment = ReflectionCommentFactory(challenge_progress=progress, user=student)
    assert handler.called

@pytest.mark.django_db
def test_progress_considered_complete_not_sent_if_mentor_reflects_first():
    handler = MagicMock()
    signals.progress_considered_complete.connect(handler) 

    student = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(student=student, mentor=mentor)
    comment = ReflectionCommentFactory(challenge_progress=progress, user=mentor)
    assert not handler.called
