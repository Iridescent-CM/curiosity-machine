from django.db import models


class Theme(models.Model):
    name = models.CharField(max_length=50,blank=True)

class Step(models.Model):
    number = models.IntegerField(default=0)
    description = models.TextField(blank=True)


class Material(models.Model):
    name = models.CharField(max_length=128,blank=True)

class Question(models.Model):
    text = models.TextField(blank=True)

class Challenge(models.Model):
    name = models.CharField(max_length=128,blank=True)
    description = models.TextField(blank=True)
    about = models.TextField(blank=True)
    theme = models.OneToOneField(Theme,related_name='challenge',null=True)
    steps = models.ManyToManyField(Step, related_name="challenge", blank=True)
    material = models.ManyToManyField(Material, related_name="challenge", blank=True)
    questions = models.ManyToManyField(Question, related_name="challenge", blank=True)

