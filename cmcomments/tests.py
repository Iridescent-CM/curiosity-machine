import pytest
from challenges.factories import ProgressFactory
from challenges.tests.fixtures import progress, challenge
from curiositymachine import signals
from mentors.factories import MentorFactory
from mock import MagicMock
from students.factories import StudentFactory
from .models import Comment
from .factories import CommentFactory, ReflectionCommentFactory

@pytest.fixture
def student():
    return StudentFactory()

@pytest.fixture
def mentor():
    return MentorFactory()

@pytest.fixture
def mentor_comment(mentor, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

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

    comment = ReflectionCommentFactory(challenge_progress=progress, user=student)
    assert handler.called
