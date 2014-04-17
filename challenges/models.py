from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from videos.models import Video

class Theme(models.Model):
    name = models.TextField()

class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField()
    how_to_make_it = models.TextField() # HTML
    learn_more = models.TextField() # HTML
    students = models.ManyToManyField(User, through='Progress', null=True) #null=True here is a workaround to an apparent bug in makemigrations 2014-03-25
    mentor = models.ForeignKey(User, related_name='mentored_challenges', null=True)
    theme = models.ForeignKey(Theme, null=True)
    video = models.ForeignKey(Video, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.mentor.profile.is_mentor:
            raise ValidationError("The mentor of a challenge can not be a student")
        else:
            super(Challenge, self).save(*args, **kwargs)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User)
    started = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if Progress.objects.filter(challenge=self.challenge, student=self.student).exists():
            raise ValidationError("There is already progress by this student on this challenge")
        elif self.student.profile.is_mentor:
            raise ValidationError("Mentors can not start a challenge")
        else:
            super(Progress, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('challenges:challenge_progress', kwargs={'challenge_id': self.challenge_id, 'username': self.student.username,})
