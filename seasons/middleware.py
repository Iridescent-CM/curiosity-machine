from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import cached_property
from django.utils.timezone import now  
from django.conf import settings
from . import jobs

SESSION_KEY = "SEASON_PARTICIPATION"

class ConfiguredSeason:
    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.name = name

    @cached_property
    def slug(self):
        if self.season_configured() and self.in_season():
            return self.start.isoformat() + ' ' + self.end.isoformat() + ' ' + self.name
        else:
            return None

    def season_configured(self):
        return self.start and self.end and self.name

    def in_season(self, now=now()):
        return self.start <= now <= self.end

def get_season():
    start = settings.SEASON_START_DATETIME
    end = settings.SEASON_END_DATETIME
    name = settings.SEASON_NAME

    return ConfiguredSeason(start, end, name)

class SeasonParticipationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            season = get_season()
            if season.slug and request.session.get(SESSION_KEY, None) != season.slug:
                jobs.record_season(season, request.user)
                request.session[SESSION_KEY] = season.slug

        return None
