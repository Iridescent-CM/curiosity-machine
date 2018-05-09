from django.contrib import admin
from .models import *

class FeedbackQuestionAdmin(admin.ModelAdmin):
    class Meta:
        model = FeedbackQuestion

    list_display = ['id', 'question']
    filter_horizontal = ['challenges']

    def __init__(self, *args, **kwargs):
        fieldsets = (
            (None, {
                'fields': ('challenges', 'is_active', 'question')
            }),
        )

        self.fieldsets = fieldsets
        super().__init__(*args, **kwargs)

    def challenge_name(self, obj):
        return obj.challenges.name

class FeedbackResultAdmin(admin.ModelAdmin):
    class Meta:
        model = FeedbackResult

    list_display = ['id', 'feedback_question', 'challenge_name', 'user']

    def challenge_name(self, obj):
        return obj.challenge.name

admin.site.register(FeedbackQuestion, FeedbackQuestionAdmin)
admin.site.register(FeedbackResult, FeedbackResultAdmin)
