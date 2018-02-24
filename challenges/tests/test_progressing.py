from cmcomments.factories import *
from mentors.factories import *
from students.factories import *
from ..factories import *
from ..progressing import *
import mock
import pytest

@pytest.mark.django_db
def test_completes_progress():
    student = StudentFactory()
    progress = ProgressFactory(owner=student)
    p = Progressing(progress=progress)

    assert not p.completes_progress(CommentFactory(user=student, challenge_progress=progress))
    assert p.completes_progress(ReflectionCommentFactory(user=student, challenge_progress=progress))
    assert not p.completes_progress(ReflectionCommentFactory(user=student, challenge_progress=progress))

@pytest.mark.django_db
def test_mentor_post_does_not_complete_progress():
    student = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(owner=student, mentor=mentor)
    p = Progressing(progress=progress)

    assert not p.completes_progress(ReflectionCommentFactory(user=mentor, challenge_progress=progress))

@pytest.mark.django_db
def test_progress_completed_by_comment():
    owner = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(owner=owner, mentor=mentor)
    comment = ReflectionCommentFactory(user=owner, challenge_progress=progress)

    wrapped_owner = mock.Mock(wraps=NoopActor(owner))
    wrapped_mentor = mock.Mock(wraps=NoopActor(mentor))

    Progressing(progress=progress, owner=wrapped_owner, mentor=wrapped_mentor).on_comment(comment)

    assert not wrapped_owner.on_comment_posted.called
    assert not wrapped_mentor.on_comment_received.called
    assert wrapped_owner.on_progress_complete.called
    assert wrapped_mentor.on_progress_complete.called

@pytest.mark.django_db
def test_owner_comments():
    owner = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(owner=owner, mentor=mentor)
    comment = CommentFactory(user=owner, challenge_progress=progress)

    wrapped_owner = mock.Mock(wraps=NoopActor(owner))
    wrapped_mentor = mock.Mock(wraps=NoopActor(mentor))

    Progressing(progress=progress, owner=wrapped_owner, mentor=wrapped_mentor).on_comment(comment)

    assert wrapped_owner.on_comment_posted.called
    assert wrapped_mentor.on_comment_received.called

@pytest.mark.django_db
def test_mentor_comments():
    owner = StudentFactory()
    mentor = MentorFactory()
    progress = ProgressFactory(owner=owner, mentor=mentor)
    comment = CommentFactory(user=mentor, challenge_progress=progress)

    wrapped_owner = mock.Mock(wraps=NoopActor(owner))
    wrapped_mentor = mock.Mock(wraps=NoopActor(mentor))

    Progressing(progress=progress, owner=wrapped_owner, mentor=wrapped_mentor).on_comment(comment)

    assert wrapped_owner.on_comment_received.called
    assert wrapped_mentor.on_comment_posted.called
