from .models import Unit, Resource
from images.models import Image
from django.contrib import admin

class UnitItemInline(admin.TabularInline):
    model = Unit.challenges.through
    extra = 1

class ResourceInline(admin.StackedInline):
    model = Resource.units.through
    extra = 1

class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name','description',)
    list_display_links = ('id', 'name',)
    fields = ('name', 'description', 'overview', 'image', 'standards_alignment_image')
    inlines = [
        UnitItemInline, ResourceInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(UnitAdmin, self).get_form(request, obj, **kwargs)

class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    list_display = ('id', 'file', 'link_text',)
    list_display_links = ('id', 'file',)

admin.site.register(Unit, UnitAdmin)
admin.site.register(Resource, ResourceAdmin)