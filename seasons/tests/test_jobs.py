import pytest
from datetime import timedelta
from django.utils.timezone import now
from profiles.factories import UserFactory
from ..jobs import _record_season
from ..middleware import get_season, ConfiguredSeason
from ..models import Season, SeasonParticipation

@pytest.fixture(autouse=True)
def in_season(settings):
    settings.SEASON_START_DATETIME = now() - timedelta(days=1)
    settings.SEASON_END_DATETIME = now() + timedelta(days=1)
    settings.SEASON_NAME = "name"

@pytest.mark.django_db
def test_record_season_creates_season():
    assert Season.objects.count() == 0

    _record_season(get_season(), UserFactory().id, now())

    assert Season.objects.count() == 1

@pytest.mark.django_db
def test_record_season_reuses_season():
    assert Season.objects.count() == 0

    _record_season(get_season(), UserFactory().id, now())
    _record_season(get_season(), UserFactory().id, now())

    assert Season.objects.count() == 1

@pytest.mark.django_db
def test_record_season_connects_user_and_season():
    assert SeasonParticipation.objects.count() == 0

    user = UserFactory()
    _record_season(get_season(), user.id, now())
    user.refresh_from_db()

    assert SeasonParticipation.objects.count() == 1
    assert SeasonParticipation.objects.first().user == user
    assert user.seasons.count() == 1

@pytest.mark.django_db
def test_record_season_only_records_once_per_season():
    user = UserFactory()
    season_1 = ConfiguredSeason(now(), now(), "season 1")
    season_2 = ConfiguredSeason(now(), now(), "season 2")

    _record_season(season_1, user.id, now())
    _record_season(season_1, user.id, now())

    assert SeasonParticipation.objects.count() == 1

    _record_season(season_2, user.id, now())
    _record_season(season_2, user.id, now())

    assert SeasonParticipation.objects.count() == 2

@pytest.mark.django_db
def test_record_season_keeps_first_record():
    user = UserFactory()

    time_1 = now() - timedelta(days=1)
    time_2 = now() - timedelta(days=2)

    _record_season(get_season(), user.id, time_1)
    _record_season(get_season(), user.id, time_2)

    assert user.seasonparticipation_set.first().joined_season_at == time_1
