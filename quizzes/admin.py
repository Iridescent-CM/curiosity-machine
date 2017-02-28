from django.contrib import admin
from .models import *

class QuizAdmin(admin.ModelAdmin):
    class Meta:
        model = Quiz

    list_display = ['id', 'challenge_name']

    def __init__(self, *args, **kwargs):
        fieldsets = (
            (None, {
                'fields': ('challenge', 'is_active')
            }),
        )
        for i in range(1, 5):
            fieldsets = fieldsets + (
                ('Question %d' % i, {
                    'fields': ('question_%d' % i,) + tuple('answer_%d_%d' % (i, j) for j in range(1, 5)) + ('correct_answer_%d' % i,)
                }),
            )
        self.fieldsets = fieldsets
        super().__init__(*args, **kwargs)

    def challenge_name(self, obj):
        return obj.challenge.name

class ResultAdmin(admin.ModelAdmin):
    class Meta:
        model = Result

    list_display = ['id', 'quiz', 'challenge_name', 'user']

    def challenge_name(self, obj):
        return obj.quiz.challenge.name

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result, ResultAdmin)
