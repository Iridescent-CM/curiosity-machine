import pytest
from challenges.factories import *
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
from ..factories import *

@pytest.mark.django_db
def test_old_progress_dont_show(client):
    mentor = MentorFactory(password="password")
    client.login(username=mentor.username, password="password")

    startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
    progress = ProgressFactory(started=startdate, mentor=mentor)

    response = client.get(reverse("mentors:home"), follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 0

@pytest.mark.django_db
def test_new_progress_will_show(client):
    mentor = MentorFactory(password="password")
    client.login(username=mentor.username, password="password")

    startdate = now()
    progress = ProgressFactory(started=startdate, mentor=mentor)

    response = client.get(reverse("mentors:home"), follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 1