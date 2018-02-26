from challenges.factories import *
from challenges.progressing import Progressing
from cmcomments.factories import *
from students.factories import *
from ..factories import *
import mock
import pytest

@pytest.mark.django_db
def test_mentor_emailed_when_student_posts():
    mentor = MentorFactory()
    student = StudentFactory()
    progress = ProgressFactory(owner=student, mentor=mentor)
    comment = CommentFactory(challenge_progress=progress, user=student)
    with mock.patch("mentors.progressing.send") as send:
        Progressing(progress=progress).on_comment(comment)
        assert send.called
        assert send.call_args[1]['template_name'] == 'mentor-student-responded-to-feedback'

@pytest.mark.django_db
def test_mentor_emailed_when_student_completes_progress():
    mentor = MentorFactory()
    student = StudentFactory()
    progress = ProgressFactory(owner=student, mentor=mentor)
    comment = ReflectionCommentFactory(challenge_progress=progress, user=student)
    with mock.patch("mentors.progressing.send") as send:
        Progressing(progress=progress).on_comment(comment)
        assert send.called
        assert send.call_args[1]['template_name'] == 'mentor-student-completed-project'

