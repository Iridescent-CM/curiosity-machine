from django.contrib import admin
from .models import Module, Comment

class ModuleAdmin(admin.ModelAdmin):
    filter_horizontal = ('mentors_done',)

admin.site.register(Module, ModuleAdmin)
admin.site.register(Comment)
