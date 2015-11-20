from django.db import models
from challenges.models import Progress, Stage, Example
from django.utils.timezone import now
from django.contrib.auth.models import User
from videos.models import Video
from images.models import Image

class Comment(models.Model):
    challenge_progress = models.ForeignKey(Progress, related_name='comments')
    user = models.ForeignKey(User)
    text = models.TextField()
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="comments")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="comments")
    created = models.DateTimeField(default=now)
    read = models.BooleanField(default=False, db_index=True)
    stage = models.SmallIntegerField(choices=[(stage.value, stage.name) for stage in Stage], default=Stage.build.value)
    question_text = models.TextField(help_text="If the comment is in direct reply to a question, this will contain the full text of the question.")

    def is_featured_as_example(self):
        return Example.objects.filter(progress=self.challenge_progress, image=self.image, video=self.video).exists()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "Comment: id={id}, user_id={user_id}, text={text}".format(id=self.id, user_id=self.user_id, text=self.text[:45] + "..." if len(self.text) > 50 else self.text)
