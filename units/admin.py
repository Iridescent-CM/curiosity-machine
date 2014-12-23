from .models import Unit
from django.contrib import admin

class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name')

admin.site.register(Unit, UnitAdmin)