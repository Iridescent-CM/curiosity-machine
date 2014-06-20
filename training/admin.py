from django.contrib import admin
from .models import Module, Comment, Task
from django.contrib.auth.models import User
from images.models import Image
from cmcomments.admin import CommentAdmin

class ModuleAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class TaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('mentors_done',)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "mentors_done":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.image.source_url)
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProgressAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=False)
        elif db_field.name == "mentor":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Module, ModuleAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
