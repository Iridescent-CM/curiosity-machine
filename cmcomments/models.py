from django.db import models
from challenges.models import Progress
from django.utils.timezone import now
from django.contrib.auth.models import User
from videos.models import Video
from images.models import Image

class Comment(models.Model):
    challenge_progress = models.ForeignKey(Progress)
    user = models.ForeignKey(User)
    text = models.TextField()
    image = models.ForeignKey(Image, null=True, blank=True)
    video = models.ForeignKey(Video, null=True, blank=True)
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)