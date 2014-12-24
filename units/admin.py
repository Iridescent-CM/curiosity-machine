from .models import Unit
from django.contrib import admin

class UnitItemInline(admin.TabularInline):
    model = Unit.challenges.through
    extra = 1

class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name','description',)
    fields = ('name', 'description',)
    inlines = [
        UnitItemInline
    ]
admin.site.register(Unit, UnitAdmin)