import pytest
from datetime import timedelta
from django.utils.timezone import now, localtime
from ..middleware import SeasonMarkerConfig

today = localtime(now())
one_day = timedelta(days=1)
two_days = timedelta(days=2)

def test_season_marker_configured():
    assert not SeasonMarkerConfig(None, today, "name").season_configured()
    assert not SeasonMarkerConfig(today, None, "name").season_configured()
    assert not SeasonMarkerConfig(today, today, None).season_configured()
    assert SeasonMarkerConfig(today, today, "name").season_configured()

def test_in_season():
    assert not SeasonMarkerConfig(today + one_day, today + two_days, "name").in_season(today)
    assert SeasonMarkerConfig(today, today + one_day, "name").in_season(today)
    assert SeasonMarkerConfig(today - one_day, today + one_day, "name").in_season(today)
    assert SeasonMarkerConfig(today - one_day, today, "name").in_season(today)
    assert not SeasonMarkerConfig(today - two_days, today - one_day, "name").in_season(today)

def test_in_season_default_now():
    assert SeasonMarkerConfig(today - one_day, today + one_day, "name").in_season()

def test_slug_when_not_configured():
    assert SeasonMarkerConfig(None, None, None).slug == None

def test_slug_when_not_in_season():
    assert SeasonMarkerConfig(today + one_day, today + two_days, "name").slug == None

def test_slug_when_configured_and_in_season():
    assert "my season marker name" in SeasonMarkerConfig(today - one_day, today + one_day, "my season marker name").slug
