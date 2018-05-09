from django.db import models
from django.conf import settings
from challenges.models import Challenge
class FeedbackQuestion(models.Model):

    class Meta:
        verbose_name_plural = 'Feedback Questions'

    challenges = models.ManyToManyField(
        Challenge,
        blank=True,
        help_text="This feedback question will show up in these selected DCs",
    )

    is_active = models.BooleanField(default=False, help_text="Enable this option to show this feedback question to students")
    question = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "FeedbackQuestion: id={}".format(self.id)

    def question_text(self):
        return getattr(self, "question")

class FeedbackResult(models.Model):

    feedback_question = models.ForeignKey(FeedbackQuestion)
    challenge = models.ForeignKey(Challenge)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='feedback_question')
    answer = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "FeedbackResult: id={} feedback_question={} username={}".format(self.id, self.feedback_question.id, self.user.username)

    @property
    def comment_text(self):
        text = ""
        text += "Q: " + self.feedback_question.question_text() + "\n"
        text += "A: " + self.answer + "\n\n"
        return text
