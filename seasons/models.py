from django.db import models
from django.contrib.auth import get_user_model

class Season(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    name = models.CharField(max_length=128)
    participants = models.ManyToManyField(
        get_user_model(),
        through='SeasonParticipation',
        related_name="seasons"
    )

    class meta:
        unique_together = ("start", "end", "name")

    def __str__(self):
        return "Season: id={}, name={}".format(self.id, self.name)

class SeasonParticipation(models.Model):
    user = models.ForeignKey(get_user_model(), null=False, blank=False)
    season = models.ForeignKey(Season, null=False, blank=False)

    joined_season_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "season")

