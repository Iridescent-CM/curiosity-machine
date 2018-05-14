import pytest
from datetime import timedelta, datetime
from django.utils.timezone import now
from ..templatetags.datepills import datepill

def test_datepill_day_rounding():
    rightnow = datetime(2000, 1, 15, 12)        # noon
    today = datetime(2000, 1, 15, 0)            # midnight
    yesterday1 = datetime(2000, 1, 14, 23, 59)  # 11:59 yesterday, <24 hrs ago
    yesterday2 = datetime(2000, 1, 14, 0)       # midnight yesterday, >24 hrs ago

    assert datepill(today, now=rightnow)['text'] == "Today"
    assert datepill(yesterday1, now=rightnow)['text'] == "1 day"
    assert datepill(yesterday2, now=rightnow)['text'] == "1 day"

def test_datepill_text():
    rightnow = now()
    assert datepill(rightnow)['text'] == "Today"
    assert datepill(rightnow - timedelta(days=1))['text'] == "1 day"
    assert datepill(rightnow - timedelta(days=2))['text'] == "2 days"
    assert datepill(rightnow - timedelta(days=3))['text'] == "3 days"
    assert datepill(rightnow - timedelta(days=4))['text'] == "4 days"
    assert datepill(rightnow - timedelta(days=5))['text'] == "5 days"
    assert datepill(rightnow - timedelta(days=6))['text'] == "6 days"
    assert datepill(rightnow - timedelta(days=7))['text'] == "1 week"
    assert datepill(rightnow - timedelta(days=8))['text'] == "1 week"
    assert datepill(rightnow - timedelta(days=13))['text'] == "1 week"
    assert datepill(rightnow - timedelta(days=14))['text'] == "2 weeks"
    assert datepill(rightnow - timedelta(days=15))['text'] == "2 weeks"
    assert datepill(rightnow - timedelta(days=29))['text'] == "2 weeks"
    assert datepill(rightnow - timedelta(days=30))['text'] == "1+ month"

def test_datepill_colors():
    rightnow = now()
    assert datepill(rightnow)['color'] == "success"
    assert datepill(rightnow - timedelta(days=1))['color'] == "success"
    assert datepill(rightnow - timedelta(days=2))['color'] == "success"
    assert datepill(rightnow - timedelta(days=3))['color'] == "success"
    assert datepill(rightnow - timedelta(days=4))['color'] == "success"
    assert datepill(rightnow - timedelta(days=5))['color'] == "warning"
    assert datepill(rightnow - timedelta(days=6))['color'] == "warning"
    assert datepill(rightnow - timedelta(days=7))['color'] == "warning"
    assert datepill(rightnow - timedelta(days=13))['color'] == "warning"
    assert datepill(rightnow - timedelta(days=14))['color'] == "purple"
    assert datepill(rightnow - timedelta(days=30))['color'] == "purple"
