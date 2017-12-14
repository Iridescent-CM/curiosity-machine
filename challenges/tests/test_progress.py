import pytest
from challenges.factories import ProgressFactory
from challenges.models import Progress
from cmcomments.factories import ReflectionCommentFactory
from mentors.factories import MentorFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_completed():
    student = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(owner=student, mentor=mentor)

    assert not progress.completed

    ReflectionCommentFactory(user=mentor, challenge_progress=progress)

    assert not progress.completed

    ReflectionCommentFactory(user=student, challenge_progress=progress)

    assert progress.completed


