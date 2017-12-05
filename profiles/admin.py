from allauth.account.models import EmailAddress
from curiositymachine import signals
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, UserChangeForm
from django.contrib.auth.models import Group
from educators.models import EducatorProfile
from images.models import Image
from mentors.models import MentorProfile
from parents.models import ParentProfile
from students.models import StudentProfile
from .admin_utils import StudentFilter
from .models import *

admin.site.unregister(Group)

class UserExtraInline(admin.StackedInline):
    model = UserExtra
    exclude = ('first_login',)

class EducatorProfileInline(admin.StackedInline):
    model = EducatorProfile

class MentorProfileInline(admin.StackedInline):
    model = MentorProfile

class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    min_num = 1

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile

class CMUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

class UserAdminWithExtra(UserAdmin):
    form = CMUserChangeForm
    inlines = [ UserExtraInline ]
    list_display = (
        'id',
        'username',
        'email',
        'source',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
        'city',
    )
    list_display_links = ('username', 'id')
    list_filter = (
        'is_superuser',
        'is_staff',
        'extra__role',
        StudentFilter
    )
    list_select_related = ('extra',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'extra__source',)

    def source(self, obj):
        return obj.extra.source
    source.admin_order_field = "extra__source"

    def city(self, obj):
        return User.cast(obj).profile.city
    city.admin_order_field = "profile__city"

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        else:
            instances = [UserExtraInline(self.model, self.admin_site),]
            if hasattr(obj, "extra"):
                if obj.extra.role == UserRole.educator.value:
                    instances.append(EducatorProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.mentor.value:
                    instances.append(MentorProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.parent.value:
                    instances.append(ParentProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.student.value:
                    instances.append(StudentProfileInline(self.model, self.admin_site))
            return instances

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'email' in form.changed_data:
            emailobj = EmailAddress.objects.add_email(request, obj, obj.email, confirm=True)
            emailobj.set_as_primary()

    def save_related(self, request, form, formsets, change):
        obj = form.instance
        if hasattr(obj, 'extra'):
            role = UserRole(obj.extra.role)
            if role.profile_attr and not hasattr(obj, role.profile_attr):
                role.profile_class.objects.create(user=obj)
        super().save_related(request, form, formsets, change)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminWithExtra)
