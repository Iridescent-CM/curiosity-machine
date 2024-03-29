from cmcomments.factories import *
from educators.factories import *
from memberships.factories import *
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
def test_educator_post_does_not_complete_progress():
    student = StudentFactory()
    educator = EducatorFactory()
    progress = ProgressFactory(owner=student)
    p = Progressing(progress=progress)

    assert not p.completes_progress(ReflectionCommentFactory(user=educator, challenge_progress=progress))

@pytest.mark.django_db
def test_progress_completed_by_comment():
    owner = StudentFactory()
    progress = ProgressFactory(owner=owner)
    comment = ReflectionCommentFactory(user=owner, challenge_progress=progress)

    wrapped_owner = mock.Mock(wraps=NoopActor(owner))
    wrapped_educators = mock.Mock(wraps=NoopActor())

    Progressing(
        progress=progress,
        owner=wrapped_owner,
        educators=wrapped_educators,
    ).on_comment(comment)

    assert wrapped_owner.on_progress_complete.called
    assert wrapped_educators.on_progress_complete.called

    assert not wrapped_owner.on_comment_posted.called
    assert not wrapped_educators.on_comment_received.called

@pytest.mark.django_db
def test_owner_comments():
    owner = StudentFactory()
    progress = ProgressFactory(owner=owner)
    comment = CommentFactory(user=owner, challenge_progress=progress)

    wrapped_owner = mock.Mock(wraps=NoopActor(owner))
    wrapped_educators = mock.Mock(wraps=NoopActor())

    Progressing(
        progress=progress,
        owner=wrapped_owner,
        educators=wrapped_educators,
    ).on_comment(comment)

    for actor in [wrapped_owner, wrapped_educators]:
        assert actor.on_comment.called
        assert actor.on_comment.call_args[0][0] == progress
        assert actor.on_comment.call_args[0][1] == comment

@pytest.mark.django_db
def test_base_actor_on_comment_posted():
    owner = StudentFactory()
    progress = ProgressFactory(owner=owner)
    comment = CommentFactory(user=owner, challenge_progress=progress)

    actor = BaseActor(owner)
    actor.on_comment_posted = mock.Mock()
    actor.on_comment_received = mock.Mock()

    actor.on_comment(progress, comment)
    assert actor.on_comment_posted.called
    assert not actor.on_comment_received.called

@pytest.mark.django_db
def test_base_actor_on_comment_received():
    owner = StudentFactory()
    educator = EducatorFactory()
    progress = ProgressFactory(owner=owner)
    comment = CommentFactory(user=educator, challenge_progress=progress)

    actor = BaseActor(owner)
    actor.on_comment_posted = mock.Mock()
    actor.on_comment_received = mock.Mock()

    actor.on_comment(progress, comment)
    assert not actor.on_comment_posted.called
    assert actor.on_comment_received.called

@pytest.mark.django_db
def test_progress_educators_looks_up_connected_educators():
    student = StudentFactory()
    progress=ProgressFactory(owner=student)
    ed = EducatorFactory()
    m = MembershipFactory(members=[student, ed], challenges=[progress.challenge])
    assert [pe.user.id for pe in ProgressEducators(progress).educators] == [ed.id]
    assert [pe.membership.id for pe in ProgressEducators(progress).educators] == [m.id]

@pytest.mark.django_db
def test_progress_educators_skips_memberships_without_relevant_challenge():
    student = StudentFactory()
    progress=ProgressFactory(owner=student)
    ed = EducatorFactory()
    MembershipFactory(members=[student, ed], challenges=[])
    assert not ProgressEducators(progress).educators

@pytest.mark.django_db
def test_progress_educators_skips_inactive_memberships():
    student = StudentFactory()
    progress=ProgressFactory(owner=student)
    ed = EducatorFactory()
    MembershipFactory(members=[student, ed], challenges=[], is_active=False)
    assert not ProgressEducators(progress).educators

@pytest.mark.django_db
def test_progress_educators_counts_educators_connected_in_multiple_ways():
    student = StudentFactory()
    progress=ProgressFactory(owner=student)
    ed = EducatorFactory()
    m1 = MembershipFactory(members=[student, ed], challenges=[progress.challenge])
    m2 = MembershipFactory(members=[student, ed], challenges=[progress.challenge])
    assert [pe.user.id for pe in ProgressEducators(progress).educators] == [ed.id, ed.id]
    assert set([pe.membership.id for pe in ProgressEducators(progress).educators]) == set([m1.id, m2.id])

@pytest.mark.django_db
def test_progress_educators_dispatches_to_each_educator():
    educators = [mock.MagicMock(), mock.MagicMock()]
    pe = ProgressEducators(mock.Mock(), educators=educators)

    pe.on_progress_complete(mock.Mock())
    for educator in educators:
        assert educator.on_progress_complete.called

    pe.on_comment(mock.Mock(), mock.Mock())
    for educator in educators:
        assert educator.on_comment.called

