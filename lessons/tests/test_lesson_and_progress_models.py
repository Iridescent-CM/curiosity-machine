import pytest
from families.factories import *
from ..factories import *

@pytest.mark.django_db
def test_progress_completed():
    family = FamilyFactory()
    progress = ProgressFactory(owner=family)
    assert not progress.completed

    CommentFactory(lesson_progress=progress, author=family)
    QuizResultFactory(quiz=progress.lesson.quiz, taker=family)

    assert progress.completed

@pytest.mark.django_db
def test_progress_not_completed():
    family = FamilyFactory()
    progress = ProgressFactory(owner=family)

    comment = CommentFactory(lesson_progress=progress, author=family)
    assert not progress.completed
    comment.delete()
    
    QuizResultFactory(quiz=progress.lesson.quiz, taker=family)
    assert not progress.completed