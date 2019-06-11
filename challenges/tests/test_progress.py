import pytest
from challenges.factories import ProgressFactory
from challenges.models import Progress
from cmcomments.factories import ReflectionCommentFactory
from educators.factories import EducatorFactory
from students.factories import StudentFactory

@pytest.mark.django_db
def test_completed():
    student = StudentFactory()
    educator = EducatorFactory()
    progress = ProgressFactory(owner=student)

    assert not progress.completed

    ReflectionCommentFactory(user=educator, challenge_progress=progress)

    assert not progress.completed

    ReflectionCommentFactory(user=student, challenge_progress=progress)

    assert progress.completed


