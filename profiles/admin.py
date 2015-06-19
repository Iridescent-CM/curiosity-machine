from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from images.models import Image
from .admin_utils import StudentFilter
from cmemails import deliver_email

from .models import Profile, ParentConnection

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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = (
        'is_superuser',
        'is_staff',
        'profile__is_mentor',
        'profile__is_student',
        'profile__is_educator',
        StudentFilter
    )

    def save_related(self, request, form, formsets, change):
        if len(formsets):
            profile = formsets[0].instance.profile
            if change:
                old_profile = Profile.objects.get(pk=profile.id)
                super(UserAdminWithProfile, self).save_related(request, form, formsets, change)
                if not old_profile.approved and profile.approved:
                    if profile.is_student and profile.birthday and profile.is_underage():
                        deliver_email('activation_confirmation', profile)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide ProfileInline in the add view
            if isinstance(inline, ProfileInline) and obj is None:
                continue
            yield inline.get_formset(request, obj)

class ParentConnectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'parent', 'child', 'active', 'removed']
    list_filter = ['active', 'removed']

    def parent(self, obj):
        return obj.parent_profile.user.username
    parent.admin_order_field = 'parent_profile__user__username'

    def child(self, obj):
        return obj.child_profile.user.username
    child.admin_order_field = 'child_profile__user__username'

admin.site.register(User, UserAdminWithProfile)
admin.site.register(ParentConnection, ParentConnectionAdmin)
