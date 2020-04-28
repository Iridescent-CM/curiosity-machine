import pytest
from datetime import timedelta
from django.utils.timezone import now
from profiles.factories import UserFactory
from ..jobs import _record_season_participation
from ..middleware import get_season_marker_config, SeasonMarkerConfig
from ..models import SeasonMarker, SeasonParticipation

@pytest.fixture(autouse=True)
def in_season(settings):
    settings.SEASON_MARKER_START_DATETIME = now() - timedelta(days=1)
    settings.SEASON_MARKER_END_DATETIME = now() + timedelta(days=1)
    settings.SEASON_MARKER_NAME = "name"

@pytest.mark.django_db
def test_record_season_participation_creates_season_marker():
    assert SeasonMarker.objects.count() == 0

    _record_season_participation(get_season_marker_config(), UserFactory().id, now())

    assert SeasonMarker.objects.count() == 1

@pytest.mark.django_db
def test_record_season_participation_reuses_season():
    assert SeasonMarker.objects.count() == 0

    _record_season_participation(get_season_marker_config(), UserFactory().id, now())
    _record_season_participation(get_season_marker_config(), UserFactory().id, now())

    assert SeasonMarker.objects.count() == 1

@pytest.mark.django_db
def test_record_season_participation_connects_user_and_season():
    assert SeasonParticipation.objects.count() == 0

    user = UserFactory()
    _record_season_participation(get_season_marker_config(), user.id, now())
    user.refresh_from_db()

    assert SeasonParticipation.objects.count() == 1
    assert SeasonParticipation.objects.first().user == user
    assert user.season_markers.count() == 1

@pytest.mark.django_db
def test_record_season_participation_only_records_once_per_season():
    user = UserFactory()
    season_1 = SeasonMarkerConfig(now(), now(), "season 1")
    season_2 = SeasonMarkerConfig(now(), now(), "season 2")

    _record_season_participation(season_1, user.id, now())
    _record_season_participation(season_1, user.id, now())

    assert SeasonParticipation.objects.count() == 1

    _record_season_participation(season_2, user.id, now())
    _record_season_participation(season_2, user.id, now())

    assert SeasonParticipation.objects.count() == 2

@pytest.mark.django_db
def test_record_season_participation_keeps_first_record():
    user = UserFactory()

    time_1 = now() - timedelta(days=1)
    time_2 = now() - timedelta(days=2)

    _record_season_participation(get_season_marker_config(), user.id, time_1)
    _record_season_participation(get_season_marker_config(), user.id, time_2)

    assert user.seasonparticipation_set.first().joined_season_at == time_1
