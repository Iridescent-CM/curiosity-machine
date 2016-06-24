import pytest

from challenges.models import Progress

from challenges.factories import ProgressFactory
from cmcomments.factories import ReflectionCommentFactory
from profiles.factories import StudentFactory, MentorFactory

@pytest.mark.django_db
def test_completed():
    student = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(student=student, mentor=mentor)

    assert not progress.completed

    ReflectionCommentFactory(user=mentor, challenge_progress=progress)

    assert not progress.completed

    ReflectionCommentFactory(user=student, challenge_progress=progress)

    assert progress.completed


