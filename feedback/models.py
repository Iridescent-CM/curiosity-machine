from django.db import models
from django.conf import settings
from challenges.models import Challenge

QUESTION_COUNT = 4
MAX_ANSWERS = 6
ANSWER_CHOICES = [(i, i) for i in range(1, MAX_ANSWERS+1)]

class Feedback(models.Model):

    class Meta:
        verbose_name_plural = 'Feedbacks'

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
        return "Feedback: id={}".format(self.id)

    def question_text(self):
        return getattr(self, "question")

class Result(models.Model):

    feedback = models.ForeignKey(Feedback)

    challenge = models.ForeignKey(Challenge)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='feedback')

    answer = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Result: id={} feedback={} username={}".format(self.id, self.feedback.id, self.user.username)

    @property
    def comment_text(self):
        text = ""
        text += "Q: " + self.feedback.question_text() + "\n"
        text += "A: " + self.answer + "\n\n"
        return text
