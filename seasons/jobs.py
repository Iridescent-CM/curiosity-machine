import django_rq
from django.utils.timezone import now
from .models import Season, SeasonParticipation

def record_season(config, user):
    django_rq.enqueue(_record_season, config, user.id, now())

def _record_season(config, user_id, joined_at):
    (season, created) = Season.objects.get_or_create(**config.model_fields)
    if not SeasonParticipation.objects.filter(season=season, user_id=user_id).exists():
        SeasonParticipation.objects.create(
            season=season,
            user_id=user_id,
            joined_season_at=joined_at
        )
