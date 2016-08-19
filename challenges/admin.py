from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.html import format_html
from .models import Challenge, Theme, Progress, Question, Example, Filter, Resource, ResourceFile
from .forms import ThemeForm, FilterForm
from cmcomments.models import Comment
from videos.models import Video
from images.models import Image
from profiles.models import UserRole
from django import forms
from django.db import models

User = get_user_model()

class ResourceFileInline(admin.TabularInline):
    model = ResourceFile
    extra = 1

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'challenge')
    inlines = (ResourceFileInline,)

admin.site.register(Resource, ResourceAdmin)

class ResourceInline(admin.TabularInline):
    model = Resource
    show_change_link = True
    extra = 1
    fields = ('name', 'description', 'resources')
    readonly_fields = ('name', 'description', 'resources',)

    def resources(self, instance):
        return format_html(
            "<ul>" 
            + "".join(['<li><a href="%s">%s</a></li>' % (x.file.url, str(x.file)) for x in instance.resourcefile_set.all()])
            + "</ul>"
        )
    resources.allow_tags = True

    def has_add_permission(self, request):
        return False

def make_draft(modeladmin, request, queryset):
    queryset.update(draft=True)
make_draft.short_description = "Move selected challenges to draft status"

def remove_draft(modeladmin, request, queryset):
    queryset.update(draft=False)
remove_draft.short_description = "Remove selected challenges from draft status"

def make_free(modeladmin, request, queryset):
    queryset.update(free=True)
make_free.short_description = "Mark selected challenges as free"

def remove_free(modeladmin, request, queryset):
    queryset.update(free=False)
remove_free.short_description = "Unmark selected challenges as free"

class ChallengeAdmin(admin.ModelAdmin):
    filter_horizontal = ('reflect_questions',)
    list_display = ['__str__', 'name', 'draft', 'free']
    list_filter = ['draft', 'free']
    actions = [make_draft, remove_draft, make_free, remove_free]
    inlines = (ResourceInline,)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(ChallengeAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'video':
                if request._obj_ is not None and request._obj_.video is not None:
                    kwargs["queryset"] = Video.objects.filter(source_url = request._obj_.video.source_url)
                else:
                    kwargs["queryset"] = Video.objects.none()

            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()

            if db_field.name == 'landing_image':
                if request._obj_ is not None and request._obj_.landing_image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.landing_image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super(ChallengeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class CommentInline(admin.StackedInline):
    model = Comment
    fields = ('user','text', 'stage')
    readonly_fields = ('user','text', 'stage')



class ProgressAdmin(admin.ModelAdmin):
    list_display = ('__str__','challenge_name','student_username','mentor_username',)
    inlines = [
      CommentInline
    ]

    actions = ['unclaim']
    search_fields = ('challenge__name', 'mentor__username', 'student__username', 'comments__text')

    def unclaim(self, request, queryset):
        rows_updated = queryset.update(mentor_id=None)
        if rows_updated == 1:
            message_bit = "1 progress was"
        else:
            message_bit = "%s progresses were" % rows_updated
        self.message_user(request, "%s successfully unclaimed." % message_bit)
    unclaim.short_description = """Remove/Unclaim the mentor from this Project"""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = User.objects.filter(profile__role=UserRole.student.value)
        elif db_field.name == "mentor":
            kwargs["queryset"] = User.objects.filter(profile__role=UserRole.mentor.value)
        return super(ProgressAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Progress, ProgressAdmin)


class ThemeAdmin(admin.ModelAdmin):
    form = ThemeForm

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Question)

class DefaultsToPendingApprovalFilter(admin.SimpleListFilter):
    title = 'approved'

    parameter_name = 'approved'

    def lookups(self, request, model_admin):
        return (
            (None, 'Pending (default)'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected or deleted'),
            ('all', 'All'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'approved':
            return queryset.filter(approved=True)
        elif self.value() == 'rejected':
            return queryset.filter(approved=False)
        elif self.value() == None:
            return queryset.filter(approved__isnull=True)

class ExampleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }

    list_display = ['id', '_challenge_name', '_student', '_admin_thumbnail', 'approved']
    list_filter = [DefaultsToPendingApprovalFilter]
    fields = ['progress', 'image', '_admin_thumbnail', 'approved']
    readonly_fields = ['_admin_thumbnail']
    search_fields = ['challenge__name', 'progress__student__username']

    def approve_all(modeladmin, request, queryset):
        queryset.approve()
    approve_all.short_description = "Approve selected examples and notify"

    def reject_all(modeladmin, request, queryset):
        queryset.reject()
    reject_all.short_description = "Reject selected examples and notify"

    actions = [approve_all, reject_all]

    def _challenge_name(self, obj):
        return obj.challenge.name
    _challenge_name.short_description = 'Challenge'

    def _student(self, obj):
        return obj.progress.student.username
    _student.short_description = 'Student'

    def _admin_thumbnail(self, obj):
        if obj.image:
            return u'<a href="%s"><img src="%s" height=200 /></a>' % (obj.image.url, obj.image.url)
        else:
            return u'No image'
    _admin_thumbnail.short_description = 'Thumbnail'
    _admin_thumbnail.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'video':
                if request._obj_ is not None and request._obj_.video is not None:
                    kwargs["queryset"] = Video.objects.filter(source_url = request._obj_.video.source_url)
                else:
                    kwargs["queryset"] = Video.objects.none()

            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Example, ExampleAdmin)

class FilterItemInline(admin.TabularInline):
    model = Filter.challenges.through
    extra = 1

class FilterAdmin(admin.ModelAdmin):
    form = FilterForm
    name = "Filters"
    fields = ('name', 'visible', 'color', 'header_template')
    list_display = ('id','name','visible', 'color',)
    inlines = [
        FilterItemInline
    ]

admin.site.register(Filter, FilterAdmin)
