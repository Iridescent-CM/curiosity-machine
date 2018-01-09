from django.contrib import admin
from .models import *

class LocationAdmin(admin.ModelAdmin):
    model = Location
    list_display = ['id', 'country', 'state', 'city']
    readonly_fields = ['country', 'state', 'city']

admin.site.register(Location, LocationAdmin)
