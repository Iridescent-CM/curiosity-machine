from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from videos.models import Video
from images.models import Image
from enum import Enum

class Stage(Enum): # this is used in challenge views and challenge and comment models
    plan = 1
    build = 2
    test = 3
    reflect = 4

class Theme(models.Model):
    name = models.TextField()

    def __str__(self):
        return "Theme: name={}".format(self.name)

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:95] + "..." if len(self.text) > 100 else self.text

class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField()
    how_to_make_it = models.TextField(help_text="HTML")
    learn_more = models.TextField(help_text="HTML")
    materials_list = models.TextField(help_text="HTML")
    students = models.ManyToManyField(User, through='Progress', through_fields=('challenge', 'student'), null=True, related_name="challenges") #null=True here is a workaround to an apparent bug in makemigrations 2014-03-25
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    plan_call_to_action = models.TextField(help_text="HTML")
    build_call_to_action = models.TextField(help_text="HTML")
    reflect_questions = models.ManyToManyField(Question, null=True)

    def __str__(self):
        return "Challenge: id={}, name={}".format(self.id, self.name)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User, related_name='progresses')
    started = models.DateTimeField(default=now)
    mentor = models.ForeignKey(User, related_name='mentored_progresses', null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if Progress.objects.filter(challenge=self.challenge, student=self.student).exclude(id=self.id).exists():
            raise ValidationError("There is already progress by this student on this challenge")
        if self.student.profile.is_mentor:
            raise ValidationError("Mentors can not start a challenge")
        if self.mentor and not self.mentor.profile.is_mentor:
            raise ValidationError("The mentor of a challenge can not be a student")
        else:
            super(Progress, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('challenges:challenge_progress', kwargs={'challenge_id': self.challenge_id, 'username': self.student.username,})

    def get_unread_comments_for_user(self, user):
        if user == self.mentor:
            return self.comments.filter(read=False, user=self.student)
        elif user == self.student:
            return self.comments.filter(read=False, user=self.mentor)
        else:
            return self.comments.none()

    def get_student_images(self):
        return Image.objects.filter(comment__user=self.student, comment__challenge_progress=self)

    def __str__(self):
        return "Progress: id={}, challenge_id={}, student_id={}".format(self.id, self.challenge_id, self.student_id)
