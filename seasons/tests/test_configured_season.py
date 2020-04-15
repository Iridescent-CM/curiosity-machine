import pytest
from datetime import timedelta
from django.utils.timezone import now, localtime
from ..middleware import ConfiguredSeason

today = localtime(now())
one_day = timedelta(days=1)
two_days = timedelta(days=2)

def test_season_configured():
    assert not ConfiguredSeason(None, today, "name").season_configured()
    assert not ConfiguredSeason(today, None, "name").season_configured()
    assert not ConfiguredSeason(today, today, None).season_configured()
    assert ConfiguredSeason(today, today, "name").season_configured()

def test_in_season():
    assert not ConfiguredSeason(today + one_day, today + two_days, "name").in_season(today)
    assert ConfiguredSeason(today, today + one_day, "name").in_season(today)
    assert ConfiguredSeason(today - one_day, today + one_day, "name").in_season(today)
    assert ConfiguredSeason(today - one_day, today, "name").in_season(today)
    assert not ConfiguredSeason(today - two_days, today - one_day, "name").in_season(today)

def test_in_season_default_now():
    assert ConfiguredSeason(today - one_day, today + one_day, "name").in_season()

def test_slug_when_not_configured():
    assert ConfiguredSeason(None, None, None).slug == None

def test_slug_when_not_in_season():
    assert ConfiguredSeason(today + one_day, today + two_days, "name").slug == None

def test_when_configured_and_in_season():
    assert "my season name" in ConfiguredSeason(today - one_day, today + one_day, "my season name").slug
