from django.db import models
from enum import Enum

class StaticPage(Enum):
    about = 1
    privacy = 2

class Page(models.Model):
    id = models.IntegerField(choices=[(page.value, page.name) for page in StaticPage], primary_key=True)
    title = models.CharField(max_length=70, help_text="title of the page, in one line of plain text") # max_length based on Google maximum visible length for titles
    text = models.TextField(help_text="contents of the page, in HTML")

    def __str__(self):
        return "Page: {}".format(self.title)
