from django.contrib import admin
from django.contrib.auth.models import User
from .models import Challenge, Theme, Progress, Question, Example, Filter
from .forms import ThemeForm, FilterForm
from cmcomments.models import Comment
from videos.models import Video
from images.models import Image
from django import forms
from django.db import models

class ChallengeAdmin(admin.ModelAdmin):
    filter_horizontal = ('reflect_questions',)

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
            kwargs["queryset"] = User.objects.filter(profile__is_student=True)
        elif db_field.name == "mentor":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=True)
        return super(ProgressAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Progress, ProgressAdmin)


class ThemeAdmin(admin.ModelAdmin):
    form = ThemeForm

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Question)

class ExampleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }

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
    fields = ('name', 'visible', 'color',)
    list_display = ('id','name','visible', 'color',)
    inlines = [
        FilterItemInline
    ]

admin.site.register(Filter, FilterAdmin)
