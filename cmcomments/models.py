from django.db import models
from challenges.models import Progress
from django.utils.timezone import now
from django.contrib.auth.models import User

class Comment(models.Model):
    challenge_progress = models.ForeignKey(Progress)
    user = models.ForeignKey(User)
    text = models.TextField()
    image = models.URLField(max_length=2083, null=True, blank=True)
    video = models.URLField(max_length=2083, null=True, blank=True)
    created = models.DateTimeField(default=now)

    class Meta:
        ordering = ('-created',)