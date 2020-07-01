from django.db import models
from django.conf import settings
from challenges.models import Challenge

QUESTION_COUNT = 4
MAX_ANSWERS = 6
ANSWER_CHOICES = [(i, i) for i in range(1, MAX_ANSWERS+1)]

class Quiz(models.Model):
    """
    Horrendously stupid quiz model for quick experiment
    """

    class Meta:
        verbose_name_plural = 'Quizzes'

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False, help_text="Enable this option to show this quiz to students")

    question_1 = models.TextField(null=True, blank=True)
    answer_1_1 = models.TextField(null=True, blank=True)
    answer_1_2 = models.TextField(null=True, blank=True)
    answer_1_3 = models.TextField(null=True, blank=True)
    answer_1_4 = models.TextField(null=True, blank=True)
    answer_1_5 = models.TextField(null=True, blank=True)
    answer_1_6 = models.TextField(null=True, blank=True)
    correct_answer_1 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True, blank=True)

    question_2 = models.TextField(null=True, blank=True)
    answer_2_1 = models.TextField(null=True, blank=True)
    answer_2_2 = models.TextField(null=True, blank=True)
    answer_2_3 = models.TextField(null=True, blank=True)
    answer_2_4 = models.TextField(null=True, blank=True)
    answer_2_5 = models.TextField(null=True, blank=True)
    answer_2_6 = models.TextField(null=True, blank=True)
    correct_answer_2 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True, blank=True)

    question_3 = models.TextField(null=True, blank=True)
    answer_3_1 = models.TextField(null=True, blank=True)
    answer_3_2 = models.TextField(null=True, blank=True)
    answer_3_3 = models.TextField(null=True, blank=True)
    answer_3_4 = models.TextField(null=True, blank=True)
    answer_3_5 = models.TextField(null=True, blank=True)
    answer_3_6 = models.TextField(null=True, blank=True)
    correct_answer_3 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True, blank=True)

    question_4 = models.TextField(null=True, blank=True)
    answer_4_1 = models.TextField(null=True, blank=True)
    answer_4_2 = models.TextField(null=True, blank=True)
    answer_4_3 = models.TextField(null=True, blank=True)
    answer_4_4 = models.TextField(null=True, blank=True)
    answer_4_5 = models.TextField(null=True, blank=True)
    answer_4_6 = models.TextField(null=True, blank=True)
    correct_answer_4 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Quiz: id={}".format(self.id)

    def quiz_length(self):
        total = 0
        for i in range(1, QUESTION_COUNT+1):
            if getattr(self, "question_%d" % i):
                total += 1
        return total

    def question_text(self, idx):
        return getattr(self, "question_%d" % idx)

    def answer_text(self, q_idx, a_idx):
        return getattr(self, "answer_%d_%d" % (q_idx, a_idx))

    def correct_answer(self, q_idx):
        return getattr(self, "correct_answer_%d" % q_idx)

    def correct_answer_text(self, q_idx):
        return self.answer_text(q_idx, self.correct_answer(q_idx))


class Result(models.Model):

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    answer_1 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True)
    answer_2 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True)
    answer_3 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True)
    answer_4 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Result: id={} quiz={} username={}".format(self.id, self.quiz.id, self.user.username)

    @property
    def score(self):
        score = 0
        for i in range(1, self.quiz.quiz_length()+1):
            if self.answer_correct(i):
                score += 1
        return score

    @property
    def score_text(self):
        return "%d/%d Correct" % (self.score, self.quiz.quiz_length())

    @property
    def comment_text(self):
        text = ""
        for i in range(1, QUESTION_COUNT+1):
            if self.selected_answer(i) is not None:
                text += "Q: " + self.quiz.question_text(i) + "\n"
                text += "A: " + self.quiz.answer_text(i, self.selected_answer(i)) + "\n\n"
        return text

    def selected_answer(self, idx):
        return getattr(self, "answer_%d" % idx)

    def answer_correct(self, idx):
        return self.quiz.correct_answer(idx) == self.selected_answer(idx)
