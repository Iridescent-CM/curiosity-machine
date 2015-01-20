from .models import Unit
from images.models import Image
from django.contrib import admin

class UnitItemInline(admin.TabularInline):
    model = Unit.challenges.through
    extra = 1

class UnitAdmin(admin.ModelAdmin):
    model = Unit
    list_display = ('id','name','description',)
    fields = ('name', 'description', 'overview', 'image', 'standards_alignment_image', )
    inlines = [
        UnitItemInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(UnitAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Unit, UnitAdmin)