from challenges.factories import *
from challenges.progressing import Progressing
from cmcomments.factories import *
from educators.factories import *
from ..factories import *
import mock
import pytest

@pytest.mark.django_db
def test_student_emailed_when_educator_posts():
    educator = EducatorFactory()
    student = StudentFactory()
    progress = ProgressFactory(owner=student)
    comment = CommentFactory(challenge_progress=progress, user=educator)
    with mock.patch("students.progressing.send") as send:
        Progressing(progress=progress).on_comment(comment)
        assert send.called
        assert send.call_args[1]['template_name'] == 'student-mentor-feedback'

