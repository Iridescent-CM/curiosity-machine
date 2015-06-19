from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from images.models import Image
from .admin_utils import StudentFilter
from cmemails import deliver_email

from .models import Profile, ParentConnection

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

admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)

class ParentConnectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'parent', 'child', 'active', 'removed']
    list_filter = ['active', 'removed']

    def parent(self, obj):
        return obj.parent_profile.user.username
    parent.admin_order_field = 'parent_profile__user__username'

    def child(self, obj):
        return obj.child_profile.user.username
    child.admin_order_field = 'child_profile__user__username'

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
        'shown_intro'
    ]
    list_display = ['user', 'id']
    
    def get_queryset(self, request):
        qs = super(ParentAdmin, self).get_queryset(request)
        return qs.filter(is_parent=True)

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
        'shown_intro'
    ]
    list_display = ['user', 'id']

    def get_queryset(self, request):
        qs = super(EducatorAdmin, self).get_queryset(request)
        return qs.filter(is_educator=True)

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
        'shown_intro'
    ]
    list_display = ['user', 'id', 'is_underage']

    def get_queryset(self, request):
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.filter(is_student=True)

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
        'shown_intro'
    ]
    list_display = ['user', 'id']

    def get_queryset(self, request):
        qs = super(MentorAdmin, self).get_queryset(request)
        return qs.filter(is_mentor=True)

admin.site.register(Mentor, MentorAdmin)
