from django.contrib import admin
from .models import *
import shlex

class LocationAdmin(admin.ModelAdmin):
    model = Location
    list_display = ['id', 'country', 'state', 'city']
    readonly_fields = ['country', 'state', 'city']
    search_fields = ['city', 'country', 'state']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        for bit in shlex.split(search_term):
            try:
                state_lookup = pycountry.subdivisions.lookup(bit)
                queryset |= self.model.objects.filter(state=state_lookup.code)
            except LookupError:
                pass

            try:
                country_lookup = pycountry.countries.lookup(bit)
                queryset |= self.model.objects.filter(country=country_lookup.alpha_2)
            except LookupError:
                pass

        return queryset, use_distinct

admin.site.register(Location, LocationAdmin)
