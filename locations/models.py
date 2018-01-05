from django.db import models
from operator import itemgetter
import pycountry

COUNTRY_CHOICES = sorted(
    ((c.alpha_2, c.name) for c in pycountry.countries),
    key=itemgetter(1)
)
US_STATE_CHOICES = sorted(
    ((d.code, d.name) for d in pycountry.subdivisions.get(country_code='US') if d.type == "State" or d.type == "District"),
    key=itemgetter(1)
)

class Location(models.Model):
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        default='US',
    )
    state = models.CharField(
        null=True,
        blank=True,
        max_length=5,
        choices=US_STATE_CHOICES,
    )
    city = models.TextField()


    def __str__(self):
        country = "country=%s, " % pycountry.countries.get(alpha_2=self.country).name
        state = ""
        if self.state:
            state = "state=%s, " % pycountry.subdivisions.get(code=self.state).name
        city = "city=%s" % self.city
        return country + state + city
