import pytest
from datetime import timedelta
from django.utils.timezone import now, localtime
from ..middleware import SeasonConfig

today = localtime(now())
one_day = timedelta(days=1)
two_days = timedelta(days=2)

def test_season_configured():
    assert not SeasonConfig(None, today, "name").season_configured()
    assert not SeasonConfig(today, None, "name").season_configured()
    assert not SeasonConfig(today, today, None).season_configured()
    assert SeasonConfig(today, today, "name").season_configured()

def test_in_season():
    assert not SeasonConfig(today + one_day, today + two_days, "name").in_season(today)
    assert SeasonConfig(today, today + one_day, "name").in_season(today)
    assert SeasonConfig(today - one_day, today + one_day, "name").in_season(today)
    assert SeasonConfig(today - one_day, today, "name").in_season(today)
    assert not SeasonConfig(today - two_days, today - one_day, "name").in_season(today)

def test_in_season_default_now():
    assert SeasonConfig(today - one_day, today + one_day, "name").in_season()

def test_slug_when_not_configured():
    assert SeasonConfig(None, None, None).slug == None

def test_slug_when_not_in_season():
    assert SeasonConfig(today + one_day, today + two_days, "name").slug == None

def test_when_configured_and_in_season():
    assert "my season name" in SeasonConfig(today - one_day, today + one_day, "my season name").slug
