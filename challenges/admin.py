from django.contrib import admin
from django.contrib.auth.models import User
from .models import Challenge, Theme, Progress, Question, Example
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'comments':
                kwargs["queryset"] = self.current_object(kwargs['request'], Comment)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def current_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return model.objects.get(challenge_progress_id=object_id)

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('__str__','challenge_name','student_username','mentor_username',)
    inlines = [
      CommentInline
    ]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=False)
        elif db_field.name == "mentor":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=True)
        return super(ProgressAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Progress, ProgressAdmin)

class ThemeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }

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