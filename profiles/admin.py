from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from curiositymachine import signals
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Q
from educators.models import EducatorProfile
from families.models import FamilyProfile
from functools import reduce
from images.models import Image
from locations.models import Location
from mentors.models import MentorProfile
from parents.models import ParentProfile
from students.models import StudentProfile
from .models import *
import operator
import shlex

admin.site.unregister(Group)

class UserExtraForm(forms.ModelForm):
    class Meta:
        model = UserExtra
        exclude = []

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if "approved" in self.changed_data and obj.approved:
            if obj.is_student:
                signals.account_activation_confirmed.send(sender=obj.user)
            elif obj.is_mentor:
                signals.completed_training.send(sender=obj.user)
        return obj

class UserExtraInline(admin.StackedInline):
    model = UserExtra
    form = UserExtraForm
    exclude = ('first_login',)

class EducatorProfileInline(admin.StackedInline):
    model = EducatorProfile
    raw_id_fields = ['image', 'location']

class MentorProfileInline(admin.StackedInline):
    model = MentorProfile
    raw_id_fields = [
        'image',
        'about_me_image',
        'about_research_image',
        'about_me_video',
        'about_research_video',
    ]

class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    raw_id_fields = ['image']
    min_num = 1

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    raw_id_fields = ['image']

class FamilyProfileInline(admin.StackedInline):
    model = FamilyProfile
    raw_id_fields = ['image', 'location']

class CMUsernameMixin():
    def clean_username(self):
        value = self.cleaned_data["username"]
        if self.has_changed() and "username" in self.changed_data:
            # enforce some allauth validation, uniqueness in particular
            value = get_adapter().clean_username(value)
        return value

class CMUserChangeForm(CMUsernameMixin, UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

class CMUserCreationForm(CMUsernameMixin, UserCreationForm):
    pass

class UserAdminWithExtra(UserAdmin):
    form = CMUserChangeForm
    add_form = CMUserCreationForm
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
        'location_city',
        'location_state',
        'location_country',
    )
    list_display_links = ('username', 'id')
    list_filter = (
        'is_superuser',
        'is_staff',
        'extra__role',
    )
    list_select_related = ('extra',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'extra__source',)

    def get_search_results(self, request, initial_qs, search_term):
        search_qs, use_distinct = super().get_search_results(request, initial_qs, search_term)

        or_queries = []

        # lookup the search term to see if it's a country name or state name
        for profile in ['educatorprofile', 'familyprofile']:
            value = Location.lookup_state_by(search_term)
            if value:
                or_queries.append(Q(**{profile + "__location__state":value}))

            value = Location.lookup_country_by(search_term)
            if value:
                or_queries.append(Q(**{profile + "__location__country":value}))

        # search all the many places city data could be stored
        for bit in shlex.split(search_term):
            for profile in ['studentprofile', 'educatorprofile', 'mentorprofile', 'parentprofile']:
                or_queries.append(Q(**{profile + "__city__icontains":bit}))

            for profile in ['educatorprofile', 'familyprofile']:
                or_queries.append(Q(**{profile + "__location__city__icontains":bit}))

        qs = search_qs
        if or_queries:
            qs = qs | initial_qs.filter(reduce(operator.or_, or_queries))

        return qs, use_distinct

    def source(self, obj):
        return obj.extra.source
    source.admin_order_field = "extra__source"

    def city(self, obj):
        return getattr(User.cast(obj).profile, 'city', None)

    def location_city(self, obj):
        location = getattr(User.cast(obj).profile, 'location', None)
        if location:
            return location.city
        return None

    def location_country(self, obj):
        location = getattr(User.cast(obj).profile, 'location', None)
        if location:
            return location.get_country_display()
        return None

    def location_state(self, obj):
        location = getattr(User.cast(obj).profile, 'location', None)
        if location and location.state:
            return location.get_state_display()
        return None

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        else:
            instances = [UserExtraInline(self.model, self.admin_site),]
            if hasattr(obj, "extra"):
                # FIXME: this can be done with a dictionary or something like that
                if obj.extra.role == UserRole.educator.value:
                    instances.append(EducatorProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.mentor.value:
                    instances.append(MentorProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.parent.value:
                    instances.append(ParentProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.student.value:
                    instances.append(StudentProfileInline(self.model, self.admin_site))
                if obj.extra.role == UserRole.family.value:
                    instances.append(FamilyProfileInline(self.model, self.admin_site))
            return instances

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'email' in form.changed_data:
            emailobj = EmailAddress.objects.add_email(request, obj, obj.email, confirm=True)
            emailobj.set_as_primary()

    def save_related(self, request, form, formsets, change):
        obj = form.instance

        if hasattr(obj, 'extra'):
            obj.extra.check_for_profile()

        super().save_related(request, form, formsets, change)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminWithExtra)
