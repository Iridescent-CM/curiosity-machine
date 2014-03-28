from django.db import models
from challenges.models import Progress
from django.contrib.auth.models import User

class Comment(models.Model):
   challenge_progress = models.ForeignKey(Progress)
   user = models.ForeignKey(User)
   text = models.TextField()
