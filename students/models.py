from datetime import date
from django.db import models
from django.urls import reverse
from profiles.models import BaseProfile

class StudentProfile(BaseProfile):
    birthday = models.DateField(blank=True,null=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)

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
