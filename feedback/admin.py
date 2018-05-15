from django.contrib import admin
from .models import *

class FeedbackQuestionAdmin(admin.ModelAdmin):
    class Meta:
        model = FeedbackQuestion

    list_display = ['id', 'question']

class FeedbackResultAdmin(admin.ModelAdmin):
    class Meta:
        model = FeedbackResult

    list_display = ['id', 'feedback_question', 'challenge_name', 'user']

    def challenge_name(self, obj):
        return obj.challenge.name

admin.site.register(FeedbackQuestion, FeedbackQuestionAdmin)
admin.site.register(FeedbackResult, FeedbackResultAdmin)
