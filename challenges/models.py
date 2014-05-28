from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from videos.models import Video
from images.models import Image
from enum import Enum
from django.utils.safestring import mark_safe

class Stage(Enum): # this is used in challenge views and challenge and comment models
    inspiration = 0
    plan = 1
    build = 2
    test = 3
    reflect = 4

class Theme(models.Model):
    name = models.TextField()
    icon = models.TextField(max_length=64, default="icon-neuroscience", help_text=mark_safe("This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace</strong><br /><br />Additionally available are the set of icons located here: <a href='http://getbootstrap.com/components/'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example \"glyphicon glyphicon-film\" without quotes."))
    color = models.TextField(max_length=64, default="#84af49", help_text=mark_safe("Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>"))

    def __str__(self):
        return "Theme: name={}".format(self.name)

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:95] + "..." if len(self.text) > 100 else self.text

class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField(help_text="One line of plain text, shown on the inspiration page")
    how_to_make_it = models.TextField(help_text="HTML, shown in the guide")
    learn_more = models.TextField(help_text="HTML, shown in the guide")
    materials_list = models.TextField(help_text="HTML")
    students = models.ManyToManyField(User, through='Progress', through_fields=('challenge', 'student'), null=True, related_name="challenges")
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    plan_call_to_action = models.TextField(help_text="HTML, shown in the left column of the plan stage")
    build_call_to_action = models.TextField(help_text="HTML, shown in the left column of the build stage")
    plan_subheader = models.TextField(help_text="One line of plain text, shown below the plan stage header")
    build_subheader = models.TextField(help_text="One line of plain text, shown below the build stage header")
    reflect_subheader = models.TextField(help_text="One line of plain text, shown below the reflect stage header")
    reflect_questions = models.ManyToManyField(Question, null=True)

    def __str__(self):
        return "Challenge: id={}, name={}".format(self.id, self.name)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User, related_name='progresses')
    started = models.DateTimeField(default=now)
    mentor = models.ForeignKey(User, related_name='mentored_progresses', null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.DateTimeField(null=True, blank=True)
    _materials_list = models.TextField(help_text="HTML", blank=True, db_column="materials_list")

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

    @property
    def materials_list(self):
        return self._materials_list if self._materials_list else self.challenge.materials_list

    @property
    def completed(self):
        # a progress is complete once a comment has been made on the Reflect stage
        return self.comments.filter(stage=Stage.reflect.value).exists()

    def __str__(self):
        return "Progress: id={}, challenge_id={}, student_id={}".format(self.id, self.challenge_id, self.student_id)
