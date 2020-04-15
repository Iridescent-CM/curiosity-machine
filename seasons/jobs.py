import django_rq
from django.utils.timezone import now
from .models import Season, SeasonParticipation

def record_season(configured_season, user):
    django_rq.enqueue(_record_season, configured_season, user.id, now())

def _record_season(configured_season, user_id, joined_at):
    (season, created) = Season.objects.get_or_create(
        start=configured_season.start,
        end=configured_season.end,
        name=configured_season.name
    )
    if not SeasonParticipation.objects.filter(season=season, user_id=user_id).exists():
        SeasonParticipation.objects.create(
            season=season,
            user_id=user_id,
            joined_season_at=joined_at
        )
