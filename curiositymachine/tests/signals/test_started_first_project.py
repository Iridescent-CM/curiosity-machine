import mock
import pytest
from challenges.factories import *
from mentors.factories import *
from profiles.factories import *
from ... import signals

@pytest.mark.django_db
def test_called_for_project_owner():
    handler = mock.MagicMock()
    signals.started_first_project.connect(handler)

    user = UserFactory()
    first_progress = ProgressFactory(owner=user)

    assert not handler.called

    first_progress.comments.create(user=user, text="comment", stage=1)

    handler.assert_called_once_with(signal=signals.started_first_project, progress=first_progress, sender=user)
    handler.reset_mock()

    second_progress = ProgressFactory(owner=user)
    second_progress.comments.create(user=user, text="comment", stage=1)

    assert not handler.called

@pytest.mark.django_db
def test_not_called_for_project_mentor():
    handler = mock.MagicMock()
    signals.started_first_project.connect(handler)

    user = MentorFactory()
    first_progress = ProgressFactory(mentor=user)

    first_progress.comments.create(user=user, text="comment", stage=1)

    assert not handler.called
