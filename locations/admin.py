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
            queryset |= self.model.objects.lookup(state=bit)
            queryset |= self.model.objects.lookup(country=bit)

        return queryset, use_distinct

admin.site.register(Location, LocationAdmin)
