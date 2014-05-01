from django.db import models
from challenges.models import Progress, Stage
from django.utils.timezone import now
from django.contrib.auth.models import User
from videos.models import Video
from images.models import Image

class Comment(models.Model):
    challenge_progress = models.ForeignKey(Progress, related_name='comments')
    user = models.ForeignKey(User)
    text = models.TextField()
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="comment")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="comment")
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False)
    stage = models.SmallIntegerField(choices=[(stage.value, stage.name) for stage in Stage], default=Stage.build.value)
    question_text = models.TextField(help_text="If the comment is in direct reply to a question, this will contain the full text of the question.")

    class Meta:
        ordering = ('-created',)
