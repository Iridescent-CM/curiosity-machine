from django.db import models
from django.contrib.auth import get_user_model

class SeasonMarker(models.Model):

    class Meta:
        unique_together = ("start", "end", "name")

    start = models.DateTimeField()
    end = models.DateTimeField()
    name = models.CharField(max_length=128)
    participants = models.ManyToManyField(
        get_user_model(),
        through='SeasonParticipation',
        related_name="season_markers"
    )

    def __str__(self):
        return "SeasonMarker: id={}, name={}".format(self.id, self.name)

class SeasonParticipation(models.Model):

    class Meta:
        unique_together = ("user", "season_marker")

    user = models.ForeignKey(get_user_model(), null=False, blank=False, on_delete=models.CASCADE)
    season_marker = models.ForeignKey(SeasonMarker, null=False, blank=False, on_delete=models.CASCADE)

    joined_season_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
