from challenges.factories import *
from challenges.progressing import Progressing
from cmcomments.factories import *
from educators.factories import *
from memberships.factories import *
from ..aichallenge import *
from ..factories import *
from ..progressing import *
import mock
import pytest

@pytest.mark.django_db
def test_send_stage_completion_email_called_for_completed_stage():
    emailer = mock.Mock()

    user = FamilyFactory()
    challenges = ChallengeFactory.create_batch(4)
    progresses = [
        ProgressFactory(challenge=challenges[0], completed=True, owner=user),
        ProgressFactory(challenge=challenges[1], completed=True, owner=user)
    ]
    stages = [
        Stage(1, challenges[0:2], units=None, user_progresses=progresses),
        Stage(2, challenges[2:4], units=None, user_progresses=progresses),
    ]
    po = ProgressOwner(
        user=user,
        emailer=emailer,
        stages=stages
    )

    po.on_progress_complete(progress=progresses[1])

    assert emailer.send_stage_completion_email.called
    assert emailer.send_stage_completion_email.call_args[0][0] == stages[0]

@pytest.mark.django_db
def test_send_stage_completion_email_not_called_for_incomplete_stage():
    emailer = mock.Mock()
    user = FamilyFactory()
    challenges = ChallengeFactory.create_batch(4)
    progresses = [
        ProgressFactory(challenge=challenges[0], completed=True, owner=user),
        ProgressFactory(challenge=challenges[1], owner=user) # has progress but not completed
    ]
    stages = [
        Stage(1, challenges[0:2], units=None, user_progresses=progresses),
        Stage(2, challenges[2:4], units=None, user_progresses=progresses),
    ]
    po = ProgressOwner(
        user=user,
        emailer=emailer,
        stages=stages
    )

    po.on_progress_complete(progress=progresses[1])

    assert not emailer.send_stage_completion_email.called

@pytest.mark.django_db
def test_family_emailed_when_coach_posts():
    coach = EducatorFactory()
    family = FamilyFactory()
    progress = ProgressFactory(owner=family)
    MembershipFactory(challenges=[progress.challenge], members=[coach, family])
    comment = CommentFactory(challenge_progress=progress, user=coach)
    with mock.patch("families.progressing.send") as send:
        Progressing(progress=progress).on_comment(comment)
        assert send.called
        assert send.call_args[1]['template_name'] == 'family-account-mentor-feedback'

