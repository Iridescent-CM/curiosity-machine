from django.db import models

class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField()
    how_to_make_it = models.TextField() # HTML
    learn_more = models.TextField() # HTML
