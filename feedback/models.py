from django.db import models
from django.conf import settings


class FeedbackQuestion(models.Model):

    is_active = models.BooleanField(default=False, help_text="Enable this option to show this feedback question to students")
    question = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "FeedbackQuestion: id={} {}".format(self.id, self.question)

class FeedbackResult(models.Model):

    feedback_question = models.ForeignKey(FeedbackQuestion)
    challenge = models.ForeignKey("challenges.Challenge")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='feedback_question')
    answer = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('feedback_question','challenge','user')

    def __str__(self):
        return "FeedbackResult: id={} feedback_question={} username={}".format(self.id, self.feedback_question.id, self.user.username)
