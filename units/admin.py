from .models import Unit, Resource
from images.models import Image
from django.contrib import admin
from django import forms
from django.db import models

class UnitItemInline(admin.TabularInline):
    model = Unit.challenges.through
    extra = 1

class ResourcesItemInline(admin.TabularInline):
    model = Resource
    extra = 1


class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name','description',)
    fields = ('name', 'description', 'standards_alignment_image', )
    inlines = [
        UnitItemInline,
        ResourcesItemInline
    ]
    
    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(UnitAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'standards_alignment_image':
                if request._obj_ is not None and request._obj_.standards_alignment_image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.standards_alignment_image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super(UnitAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Unit, UnitAdmin)