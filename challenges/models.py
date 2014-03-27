from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField()
    how_to_make_it = models.TextField() # HTML
    learn_more = models.TextField() # HTML
    students = models.ManyToManyField(User, through='Progress', null=True) #null=True here is a workaround to an apparent bug in makemigrations 2014-03-25
    mentor = models.ForeignKey(User, related_name='mentored_challenges', null=True)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User)
    started = models.DateTimeField(default=now)
