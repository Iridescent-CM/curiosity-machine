from challenges.factories import *
from challenges.progressing import Progressing
from cmcomments.factories import *
from educators.factories import *
from memberships.factories import *
from ..factories import *
from ..progressing import *
import mock
import pytest

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

