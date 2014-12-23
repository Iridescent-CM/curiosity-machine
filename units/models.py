from django.db import models


class Unit(models.Model):
    name = models.TextField()

    def __str__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)

    def __repr__(self):
        return "Unit: id={}, name={}".format(self.id, self.name)