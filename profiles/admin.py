import allauth.account.models
from curiositymachine import signals
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from educators.models import EducatorProfile
from images.models import Image
from mentors.models import MentorProfile
from parents.models import ParentProfile
from students.models import StudentProfile
from .admin_utils import StudentFilter
from .models import *

admin.site.unregister(Group)

# This proxy just consolidates allauth EmailAddresses in the same admin app section
class EmailAddress(allauth.account.models.EmailAddress):
    class Meta:
        proxy = True
        verbose_name_plural = "Email addresses"

admin.site.unregister(allauth.account.models.EmailAddress)
admin.site.register(EmailAddress)

class UserExtraInline(admin.StackedInline):
    model = UserExtra
    exclude = ('first_login',)

class EmailAddressInline(admin.StackedInline):
    model = EmailAddress
    min_num = 1
    max_num = 1

class EducatorProfileInline(admin.StackedInline):
    model = EducatorProfile

class MentorProfileInline(admin.StackedInline):
    model = MentorProfile

class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    min_num = 1

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile

class UserAdminWithExtra(UserAdmin):
    inlines = [ UserExtraInline, EmailAddressInline ]
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
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
)
    readonly_fields = ('email',)
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
            instances = [UserExtraInline(self.model, self.admin_site), EmailAddressInline(self.model, self.admin_site)]
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

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminWithExtra)

class ParentConnectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'parent', 'parent_email', 'child', 'child_email', 'active', 'removed']
    list_filter = ['active', 'removed']
    search_fields = [
        'parent_profile__user__username',
        'child_profile__user__username',
        'parent_profile__user__email',
        'child_profile__user__email'
    ]

    def parent(self, obj):
        return obj.parent_profile.user.username
    parent.admin_order_field = 'parent_profile__user__username'

    def parent_email(self, obj):
        return obj.parent_profile.user.email
    parent.admin_order_field = 'parent_profile__user__email'

    def child(self, obj):
        return obj.child_profile.user.username
    child.admin_order_field = 'child_profile__user__username'

    def child_email(self, obj):
        return obj.child_profile.user.email
    child.admin_order_field = 'child_profile__user__email'

admin.site.register(ParentConnection, ParentConnectionAdmin)

class ImpactSurveyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'student_count',
        'teacher_count',
        'challenge_count',
        'hours_per_challenge',
        'in_classroom',
        'out_of_classroom',
        'created_at',
    )
    raw_id_fields = ('user',)
    readonly_fields = (
        'id',
        'user',
        'student_count',
        'teacher_count',
        'challenge_count',
        'hours_per_challenge',
        'in_classroom',
        'out_of_classroom',
        'comment',
        'created_at',
    )

admin.site.register(ImpactSurvey, ImpactSurveyAdmin)
