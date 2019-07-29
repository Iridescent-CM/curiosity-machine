import pytest
from ..factories import *
from ..presenters import *

@pytest.mark.django_db
def test_next_lesson_url():
    progress1 = LessonFactory(order=1, draft=False)
    progress2 = LessonFactory(order=2, draft=False)
    progress3 = LessonFactory(order=3, draft=True)
    progress4 = LessonFactory(order=4, draft=False)

    assert TabbedLesson(progress1).next_lesson_url == '/lessons/lesson/%d/' % progress2.id
    assert TabbedLesson(progress2).next_lesson_url == '/lessons/lesson/%d/' % progress4.id
    assert not TabbedLesson(progress4).next_lesson_url
