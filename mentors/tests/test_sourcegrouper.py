import pytest
from challenges.factories import ProgressFactory
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from ..grouping import *

@pytest.mark.django_db
def test_groups_by_source():
    ProgressFactory.create_batch(3, comment=True)
    ProgressFactory.create_batch(3, owner__extra__source='One', comment=True)
    ProgressFactory.create_batch(3, owner__extra__source='Two', comment=True)
    ProgressFactory.create_batch(3, started=now()-relativedelta(days=3), owner__extra__source='Two', comment=True)
    groups = SourceGrouper().group(startdate=now() - relativedelta(months=3))
    assert len(groups) == 3
    assert set([g.title for g in groups]) == set(['One', 'Two', 'Other'])

@pytest.mark.django_db
def test_stops_at_startdate():
    today = now()
    first = ProgressFactory(started=today, comment=True)
    second = ProgressFactory(started=today-relativedelta(days=10), comment=True)

    groups = SourceGrouper().group(startdate=today - relativedelta(days=5))
    assert len(groups) == 1
