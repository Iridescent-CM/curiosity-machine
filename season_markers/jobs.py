import django_rq
from django.utils.timezone import now
from .models import SeasonMarker, SeasonParticipation

def record_season_participation(config, user):
    django_rq.enqueue(_record_season_participation, config, user.id, now())

def _record_season_participation(config, user_id, joined_at):
    (season_marker, created) = SeasonMarker.objects.get_or_create(**config.model_fields)
    if not SeasonParticipation.objects.filter(season_marker=season_marker, user_id=user_id).exists():
        SeasonParticipation.objects.create(
            season_marker=season_marker,
            user_id=user_id,
            joined_season_at=joined_at
        )
