from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import cached_property
from django.utils.timezone import now  
from django.conf import settings
from . import jobs

SESSION_KEY = "SEASON_PARTICIPATION"

class SeasonMarkerConfig:
    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.name = name

    @cached_property
    def slug(self):
        if self.in_season():
            return self.start.isoformat() + ' ' + self.end.isoformat() + ' ' + self.name
        else:
            return None

    def season_configured(self):
        return bool(self.start and self.end and self.name)

    def in_season(self, now=now()):
        return bool(self.season_configured() and self.start <= now <= self.end)

    @cached_property
    def model_fields(self):
        return {
            'start': self.start,
            'end': self.end,
            'name': self.name
        }


def get_season_marker_config():
    start = settings.SEASON_MARKER_START_DATETIME
    end = settings.SEASON_MARKER_END_DATETIME
    name = settings.SEASON_MARKER_NAME

    return SeasonMarkerConfig(start, end, name)

class SeasonParticipationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            config = get_season_marker_config()
            if config.slug and request.session.get(SESSION_KEY, None) != config.slug:
                jobs.record_season_participation(config, request.user)
                request.session[SESSION_KEY] = config.slug

        return None
