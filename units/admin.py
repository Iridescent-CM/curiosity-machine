import os

from .models import Unit, Resource
from images.models import Image
from django.contrib import admin

class UnitItemInline(admin.TabularInline):
    model = Unit.challenges.through
    ordering = ('display_order',)
    extra = 1

class ResourceInline(admin.StackedInline):
    model = Resource.units.through
    extra = 1

class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name','description', 'draft')
    list_display_links = ('id', 'name',)
    list_filter = ['draft']
    fields = ('name', 'description', 'overview', 'image', 'standards_alignment_image', 'draft')
    inlines = [
        UnitItemInline, ResourceInline
    ]

class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    list_display = ('id', 'filename', 'link_text',)
    list_display_links = ('id', 'filename',)

    def filename(self, obj):
        return os.path.basename(obj.file)

admin.site.register(Unit, UnitAdmin)
admin.site.register(Resource, ResourceAdmin)