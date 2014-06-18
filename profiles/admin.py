from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from images.models import Image

from .models import Profile

admin.site.unregister(User)

class ProfileInline(admin.StackedInline):
    model = Profile

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.profile.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.profile.image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class UserAdminWithProfile(UserAdmin):
    inlines = [ ProfileInline, ]

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide ProfileInline in the add view
            if isinstance(inline, ProfileInline) and obj is None:
                continue
            yield inline.get_formset(request, obj)

admin.site.register(User, UserAdminWithProfile)
