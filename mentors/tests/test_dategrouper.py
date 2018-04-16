import pytest
from challenges.factories import ProgressFactory
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now, get_current_timezone
from ..grouping import *

@pytest.mark.django_db
def test_groups_by_date():
    today = now()
    first = ProgressFactory(started=today, comment=True)
    second = ProgressFactory(started=today-relativedelta(days=1), comment=True)
    third = ProgressFactory(started=today-relativedelta(days=1), comment=True)

    groups = DateGrouper().group(startdate=today - relativedelta(weeks=1))
    assert len(groups) == 2

    ctz = get_current_timezone()
    assert groups[0].title == ctz.normalize(first.started.astimezone(ctz)).date().strftime("%B %d, %Y")
    assert groups[0].unclaimed == 1
    assert groups[1].title == ctz.normalize(second.started.astimezone(ctz)).date().strftime("%B %d, %Y")
    assert groups[1].unclaimed == 2

@pytest.mark.django_db
def test_stops_at_startdate():
    today = now()
    first = ProgressFactory(started=today, comment=True)
    second = ProgressFactory(started=today-relativedelta(days=10), comment=True)

    groups = DateGrouper().group(startdate=today - relativedelta(days=5))
    assert len(groups) == 1