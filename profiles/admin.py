from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from images.models import Image
from .admin_utils import StudentFilter
from cmemails import deliver_email
from curiositymachine import signals

from .models import Profile, ParentConnection, UserRole

User = get_user_model()

class ProfileInline(admin.StackedInline):
    model = Profile
    raw_id_fields = ('image', 'about_me_image', 'about_me_video', 'about_research_image', 'about_research_video')
    exclude = ('first_login',)

class UserAdminWithProfile(UserAdmin):
    inlines = [ ProfileInline, ]
    list_display = ('username', 'email', 'source', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = (
        'is_superuser',
        'is_staff',
        'profile__role',
        StudentFilter
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__source')

    def source(self, obj):
        return obj.profile.source
    source.admin_order_field = "profile__source"

    def save_related(self, request, form, formsets, change):
        if len(formsets):
            profile = formsets[0].instance.profile
            if change:
                old_profile = Profile.objects.get(pk=profile.id)
                super(UserAdminWithProfile, self).save_related(request, form, formsets, change)
                if not old_profile.approved and profile.approved:
                    if profile.is_student and profile.birthday and profile.is_underage():
                        signals.underage_activation_confirmed.send(sender=request.user, account=profile.user)
                    elif profile.is_mentor:
                        signals.completed_training.send(sender=profile.user, approver=request.user)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide ProfileInline in the add view
            if isinstance(inline, ProfileInline) and obj is None:
                continue
            yield inline.get_formset(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)

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

class Parent(Profile):
    class Meta:
        proxy = True

class ParentChildInline(admin.TabularInline):
    model = Profile.child_profiles.through
    fk_name = "parent_profile"
    extra = 0

class ParentAdmin(admin.ModelAdmin):
    inlines = [ ParentChildInline ]
    fields = [
        'user',
        'city',
        'image',
        'approved',
        'last_active_on',
        'last_inactive_email_sent_on',
    ]
    raw_id_fields = ['image']
    list_display = ['user', 'email', 'id']
    search_fields = [
        'user__username',
        'user__email',
    ]

    def get_queryset(self, request):
        qs = super(ParentAdmin, self).get_queryset(request)
        return qs.filter(role=UserRole.parent.value)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = "user__email"

admin.site.register(Parent, ParentAdmin)

class Educator(Profile):
    class Meta:
        proxy = True

class EducatorAdmin(admin.ModelAdmin):
    fields = [
        'user',
        'city',
        'image',
        'approved',
        'last_active_on',
        'last_inactive_email_sent_on',
    ]
    raw_id_fields = ['image']
    list_display = ['user', 'email', 'id']
    search_fields = [
        'user__username',
        'user__email',
    ]

    def get_queryset(self, request):
        qs = super(EducatorAdmin, self).get_queryset(request)
        return qs.filter(role=UserRole.educator.value)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = "user__email"

admin.site.register(Educator, EducatorAdmin)

class Student(Profile):
    class Meta:
        proxy = True

class ChildParentInline(admin.TabularInline):
    model = Profile.child_profiles.through
    fk_name = "child_profile"
    extra = 0

class StudentAdmin(admin.ModelAdmin):
    inlines = [ ChildParentInline ]
    fields = [
        'user',
        'city',
        'birthday',
        'parent_first_name',
        'parent_last_name',
        'image',
        'approved',
        'last_active_on',
        'last_inactive_email_sent_on',
    ]
    raw_id_fields = ['image']
    list_display = ['user', 'email', 'id', 'is_underage']
    search_fields = [
        'user__username',
        'user__email',
    ]

    def get_queryset(self, request):
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.filter(role=UserRole.student.value)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = "user__email"

admin.site.register(Student, StudentAdmin)

class Mentor(Profile):
    class Meta:
        proxy = True

class MentorAdmin(admin.ModelAdmin):
    fields = [
        'user',
        'city',
        'title',
        'employer',
        'expertise',
        'about_me',
        'about_me_image',
        'about_me_video',
        'about_research',
        'about_research_image',
        'about_research_video',
        'image',
        'approved',
        'last_active_on',
        'last_inactive_email_sent_on',
    ]
    raw_id_fields = [
        'image',
        'about_me_image',
        'about_me_video',
        'about_research_image',
        'about_research_video',
    ]
    list_display = ['user', 'email', 'id']
    search_fields = [
        'user__username',
        'user__email',
    ]

    def get_queryset(self, request):
        qs = super(MentorAdmin, self).get_queryset(request)
        return qs.filter(role=UserRole.mentor.value)

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = "user__email"

admin.site.register(Mentor, MentorAdmin)
