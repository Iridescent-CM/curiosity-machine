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

def _wrap(fn):
    def reorder_after_action(modeladmin, request, queryset):
        response = fn(modeladmin, request, queryset)
        if response:
            return response
        qs = modeladmin.get_queryset(request).order_by('order')
        order = 0
        for obj in qs.all():
            if obj.order != order:
                obj.order = order
                obj.save(update_fields=['order'])
            order += 1
        return None

    return reorder_after_action

class LessonAdmin(OrderedModelAdmin):
    form = LessonAdminForm
    save_as = True
    save_on_top = True
    list_display = ('id', 'title', 'move_up_down_links', 'order')
    raw_id_fields = ('card_image', 'quiz')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            old = actions['delete_selected']
            actions['delete_selected'] = (_wrap(old[0]), old[1], old[2])
        return actions

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

class QuizAdmin(admin.ModelAdmin):
    model = Quiz
    list_display = ('id', 'question_1', 'created_at')

class QuizResultAdmin(admin.ModelAdmin):
    model = QuizResult
    list_display = ('id', 'question_1', 'answer_1', 'taker', 'created_at')

    def question_1(self, obj):
        return obj.quiz.question_1

admin.site.register(Lesson, LessonAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizResult, QuizResultAdmin)
