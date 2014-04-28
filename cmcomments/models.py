from django.db import models
from challenges.models import Progress
from django.utils.timezone import now
from django.contrib.auth.models import User
from videos.models import Video
from images.models import Image

class Comment(models.Model):
    challenge_progress = models.ForeignKey(Progress, related_name='comments')
    user = models.ForeignKey(User)
    text = models.TextField()
    image = models.ForeignKey(Image, null=True, blank=True)
    video = models.ForeignKey(Video, null=True, blank=True)
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)

    PLAN = 1
    BUILD = 2
    TEST = 3
    STAGE_CHOICES = (
        (PLAN, 'plan'),
        (BUILD, 'build'),
        (TEST, 'test'),
    )
    stage = models.SmallIntegerField(choices=STAGE_CHOICES, default=BUILD)

    class Meta:
        ordering = ('-created',)
