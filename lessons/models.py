from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from images.models import Image
from ordered_model.models import OrderedModel

class Lesson(OrderedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(help_text="Description shown on the dashboard", null=True, blank=True)
    card_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, help_text="Image shown on the dashboard")
    start = models.TextField(blank=True)
    inspiration = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    build = models.TextField(blank=True)
    further = models.TextField(blank=True)
    quiz = models.ForeignKey('Quiz', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta(OrderedModel.Meta):
        pass

    def get_absolute_url(self):
        return reverse("lessons:lesson-detail", kwargs={
            "pk": self.id,
        })

    def __str__(self):
        return "Lesson: id={} title={}".format(self.id, self.title)

class Progress(models.Model):
    lesson = models.ForeignKey(Lesson)
    owner = models.ForeignKey(get_user_model(), related_name='lesson_progresses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "progresses"
        unique_together = ('lesson', 'owner',)

    def __str__(self):
        return "Lesson Progress: id={} owner={} title={}".format(self.id, self.owner, self.lesson.title)

    @property
    def object_id(self):
        return self.lesson_id

    @property
    def completed(self):
        return self.comment_set.all().exists()

class Comment(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='lesson_comments')
    lesson_progress = models.ForeignKey(Progress)
    text = models.TextField(null=True, blank=True)

    upload_content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    upload_id = models.PositiveIntegerField(null=True, blank=True)
    upload = GenericForeignKey('upload_content_type', 'upload_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Lesson Comment: id={} author={} lesson={}".format(self.id, self.author, self.lesson_progress.lesson)

class Quiz(models.Model):

    class Meta:
        verbose_name_plural = 'Quizzes'

    question_1 = models.TextField()
    answer_1_1 = models.TextField()
    answer_1_2 = models.TextField()
    answer_1_3 = models.TextField()
    correct_answer_1 = models.PositiveSmallIntegerField()
    explanation_1 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Quiz: id={} question={}".format(self.id, self.question_1)

class QuizResult(models.Model):
    taker = models.ForeignKey(get_user_model())
    quiz = models.ForeignKey(Quiz)
    answer_1 = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Quiz Result: id={} quiz={} taker={}".format(self.id, self.quiz_id, self.taker_id)

    @property
    def correct(self):
        return self.answer_1 == self.quiz.correct_answer_1
