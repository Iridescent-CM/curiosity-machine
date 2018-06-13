from django.contrib import admin
from django import forms
from django_ace import AceWidget
from .models import *

ACECONFIG = {
    "width": "800px",
    "wordwrap": True
}

class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        exclude = []
        widgets = {
            'inspiration': AceWidget(mode="html", **ACECONFIG),
            'plan': AceWidget(mode="html", **ACECONFIG),
            'build': AceWidget(mode="html", **ACECONFIG),
            'reflect': AceWidget(mode="html", **ACECONFIG),
            'further': AceWidget(mode="html", **ACECONFIG),
        }

    class Media:
        js = ('js/ace_widget.js',)

class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    save_as = True
    save_on_top = True
    list_display = ('id', 'title')

class ProgressAdmin(admin.ModelAdmin):
    model = Progress
    list_display = ('id', 'owner', 'lesson', 'created_at', 'updated_at')

class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('id', 'author', '_progress_owner', '_lesson_title', '_lesson_id')

    def _progress_owner(self, obj):
        return obj.lesson_progress.owner

    def _lesson_title(self, obj):
        return obj.lesson_progress.lesson.title

    def _lesson_id(self, obj):
        return obj.lesson_progress.lesson.id

admin.site.register(Lesson, LessonAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Comment, CommentAdmin)
