from datetime import date
from django.db import models
from django.urls import reverse
from images.models import Image
from profiles.models import BaseProfile

class StudentProfile(BaseProfile):
    birthday = models.DateField(blank=False,null=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    city = models.TextField(blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birthday.year
            #subtract a year if birthday hasn't occurred yet
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )

    def is_underage(self):
        return self.age < 13
    is_underage.boolean = True
