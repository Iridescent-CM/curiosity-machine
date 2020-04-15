import pytest
from mock import Mock, MagicMock, patch
from datetime import timedelta
from django.utils.timezone import now
from ..middleware import SeasonParticipationMiddleware

def set_in_season(settings, name="name"):
    settings.SEASON_START_DATETIME = now() - timedelta(days=1)
    settings.SEASON_END_DATETIME = now() + timedelta(days=1)
    settings.SEASON_NAME = name

def set_no_season(settings):
    settings.SEASON_START_DATETIME = None
    settings.SEASON_END_DATETIME = None
    settings.SEASON_NAME = None

@pytest.fixture
def in_season(settings):
    set_in_season(settings)

@pytest.fixture
def no_season(settings):
    set_no_season(settings)

def test_job_not_run_when_unauthenticated(rf, in_season):
    user = Mock()
    user.is_authenticated = False

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        middleware.process_request(request)

        jobs.record_season.assert_not_called()

def test_job_run_when_authenticated(rf, in_season):
    user = Mock()
    user.is_authenticated = True

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        middleware.process_request(request)

        jobs.record_season.assert_called()

def test_job_run_once_within_session(rf, in_season):
    user = Mock()
    user.is_authenticated = True

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        middleware.process_request(request)
        middleware.process_request(request)

        jobs.record_season.assert_called_once()

def test_job_run_when_transitioning_into_season(rf, settings):
    user = Mock()
    user.is_authenticated = True

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        set_no_season(settings)
        middleware.process_request(request)
        jobs.record_season.assert_not_called()

        set_in_season(settings)
        middleware.process_request(request)
        jobs.record_season.assert_called()


def test_job_run_when_transitioning_between_seasons(rf, settings):
    user = Mock()
    user.is_authenticated = True

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        set_in_season(settings, name="season1")
        middleware.process_request(request)
        middleware.process_request(request)
        jobs.record_season.assert_called_once()

        jobs.reset_mock()

        set_in_season(settings, name="season2")
        middleware.process_request(request)
        middleware.process_request(request)
        jobs.record_season.assert_called_once()


def test_job_not_run_when_transitioning_out_of_season(rf, settings):
    user = Mock()
    user.is_authenticated = True

    request = rf.get('/')
    request.user = user
    request.session = {}

    middleware = SeasonParticipationMiddleware()

    with patch('seasons.middleware.jobs') as jobs:
        set_in_season(settings)
        middleware.process_request(request)
        jobs.record_season.assert_called()

        jobs.reset_mock()

        set_no_season(settings)
        middleware.process_request(request)
        jobs.record_season.assert_not_called()
