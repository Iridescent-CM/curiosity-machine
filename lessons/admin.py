from django.contrib import admin
from django import forms
from django_ace import AceWidget
from ordered_model.admin import OrderedModelAdmin
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
            attr: AceWidget(mode="html", **ACECONFIG)
            for attr
            in ['start', 'inspiration', 'plan', 'build', 'reflect', 'further']
        }

    class Media:
        js = ('js/ace_widget.js',)

class LessonAdmin(OrderedModelAdmin):
    form = LessonAdminForm
    save_as = True
    save_on_top = True
    list_display = ('id', 'title', 'move_up_down_links', 'order')
    raw_id_fields = ('card_image',)

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
admin.site.register(Quiz)
admin.site.register(QuizResult)
