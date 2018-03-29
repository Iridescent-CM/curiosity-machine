from curiositymachine.validators import validate_simple_latin
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

class LocationQuerySet(models.QuerySet):
    def lookup(self, **kwargs):
        if len(kwargs) != 1:
            raise TypeError("Only one criteria may be given")
        field, value = kwargs.popitem()

        if field == "state":
            code = Location.lookup_state_by(value)
            if code:
                return self.filter(state=code)
        elif field == "country":
            code = Location.lookup_country_by(value)
            if code:
                return self.filter(country=code)

        return self.none()

class Location(models.Model):
    country = models.CharField(
        max_length=2,
        choices=[(None, "Select country...")] + COUNTRY_CHOICES,
    )
    state = models.CharField(
        null=True,
        blank=True,
        max_length=5,
        choices=[(None, "Select state...")] + US_STATE_CHOICES,
    )
    city = models.TextField(
        validators=[validate_simple_latin],
    )

    objects = LocationQuerySet.as_manager()

    def __str__(self):
        country = "country=%s, " % pycountry.countries.get(alpha_2=self.country).name
        state = ""
        if self.state:
            state = "state=%s, " % pycountry.subdivisions.get(code=self.state).name
        city = "city=%s" % self.city
        return country + state + city

    @staticmethod
    def lookup_state_by(value):
        try:
            state = pycountry.subdivisions.lookup(value)
            return state.code
        except LookupError:
            return None

    @staticmethod
    def lookup_country_by(value):
        try:
            country = pycountry.countries.lookup(value)
            return country.alpha_2
        except LookupError:
            return None
