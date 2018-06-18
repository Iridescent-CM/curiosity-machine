from challenges.factories import *
from units.factories import *
from ..aichallenge import *
import pytest

def test_challenges_and_stats_without_user_progresses():
    challenges = ChallengeFactory.build_batch(5)
    stage = Stage(1, challenges, units=None)
    assert stage.objects == challenges
    assert stage.stats["total"] == 5
    assert stage.stats["completed"] == 0
    assert stage.stats["percent_complete"] == 0

@pytest.mark.django_db
def test_challenges_and_stats_with_user_progresses():
    challenges = ChallengeFactory.create_batch(5)
    progresses = [ProgressFactory(challenge=challenges[0], completed=True)]
    stage = Stage(1, challenges, units=None, user_progresses=progresses)
    assert stage.objects == challenges
    assert stage.stats["total"] == 5
    assert stage.stats["completed"] == 1
    assert stage.stats["percent_complete"] == 20 

@pytest.mark.django_db
def test_is_complete():
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, completed=True)
    assert not Stage(1, [challenge], units=None).is_complete
    assert Stage(1, [challenge], units=None, user_progresses=[progress]).is_complete

@pytest.mark.django_db
def test_from_config_pulls_units():
    units = UnitFactory.create_batch(5)
    config = {
        'challenges': [],
        'units': [u.id for u in units[1:3]]
    }
    stage = Stage.from_config(1, config=config)
    assert stage.units == units[1:3]

@pytest.mark.django_db
def test_from_config_pulls_challenges():
    challenges = ChallengeFactory.create_batch(5)
    config = {
        'challenges': [c.id for c in challenges[1:3]],
        'units': []
    }
    stage = Stage.from_config(1, config=config)
    assert stage.objects == challenges[1:3]

@pytest.mark.django_db
def test_from_config_preserves_order():
    challenges = ChallengeFactory.create_batch(5)
    order = [2, 1, 3]
    config = {
        'challenges': [challenges[idx].id for idx in order],
        'units': []
    }
    stage = Stage.from_config(1, config=config)
    assert stage.objects == [challenges[idx] for idx in order]

@pytest.mark.django_db
def test_decorates_with_progress_indicator():
    challenges = ChallengeFactory.create_batch(5)
    completed = ProgressFactory(challenge=challenges[0], completed=True)
    started = ProgressFactory(challenge=challenges[1])
    stage = Stage(1, challenges, units=None, user_progresses=[completed, started])

    assert stage.objects[0].state == "completed"
    assert stage.objects[1].state == "started"
    assert stage.objects[2].state == "not-started"

@pytest.mark.django_db
def test_has_object():
    challenges = ChallengeFactory.create_batch(5)
    challenge = ChallengeFactory()
    stage = Stage(1, challenges, units=None)
    assert stage.has_object(challenges[0])
    assert stage.has_object(challenges[0].id)
    assert not stage.has_object(challenge)
    assert not stage.has_object(challenge.id)
