from django.db import models
from django.conf import settings
from challenges.models import Challenge

ANSWER_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4))

class Quiz(models.Model):
    """
    Horrendously stupid quiz model for quick experiment
    """

    class Meta:
        verbose_name_plural = 'Quizzes'

    challenge = models.ForeignKey(Challenge)
    is_active = models.BooleanField(default=False, help_text="Enable this option to show this quiz to students")

    question_1 = models.TextField()
    answer_1_1 = models.TextField()
    answer_1_2 = models.TextField()
    answer_1_3 = models.TextField()
    answer_1_4 = models.TextField()
    correct_answer_1 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)

    question_2 = models.TextField()
    answer_2_1 = models.TextField()
    answer_2_2 = models.TextField()
    answer_2_3 = models.TextField()
    answer_2_4 = models.TextField()
    correct_answer_2 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)

    question_3 = models.TextField()
    answer_3_1 = models.TextField()
    answer_3_2 = models.TextField()
    answer_3_3 = models.TextField()
    answer_3_4 = models.TextField()
    correct_answer_3 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)

    question_4 = models.TextField()
    answer_4_1 = models.TextField()
    answer_4_2 = models.TextField()
    answer_4_3 = models.TextField()
    answer_4_4 = models.TextField()
    correct_answer_4 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)

    def __str__(self):
        return "Quiz: id={}".format(self.id)

    def question_text(self, idx):
        return getattr(self, "question_%d" % idx)

    def answer_text(self, q_idx, a_idx):
        return getattr(self, "answer_%d_%d" % (q_idx, a_idx))

    def correct_answer(self, q_idx):
        return getattr(self, "correct_answer_%d" % q_idx)

    def correct_answer_text(self, q_idx):
        return self.answer_text(q_idx, self.correct_answer(q_idx))


class Result(models.Model):

    quiz = models.ForeignKey(Quiz)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    answer_1 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)
    answer_2 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)
    answer_3 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)
    answer_4 = models.PositiveSmallIntegerField(choices=ANSWER_CHOICES)

    def __str__(self):
        return "Result: id={} quiz={} username={}".format(self.id, self.quiz.id, self.user.username)

    @property
    def score(self):
        score = 0
        for i in range(1, 5):
            if self.answer_correct(i):
                score += 1
        return score

    @property
    def score_text(self):
        return "%d/4 Correct" % self.score

    @property
    def comment_text(self):
        text = ""
        for i in range(1, 5):
            text += self.quiz.question_text(i) + "\n"
            text += self.quiz.answer_text(i, self.selected_answer(i)) + "\n"
            if self.answer_correct(i): 
                text += "Correct!\n"
            else:
                text += "Incorrect\n"
                text += "Correct answer: " + self.quiz.correct_answer_text(i) + "\n"
            text += "\n"
        return text

    def selected_answer(self, idx):
        return getattr(self, "answer_%d" % idx)

    def answer_correct(self, idx):
        return self.quiz.correct_answer(idx) == self.selected_answer(idx)
