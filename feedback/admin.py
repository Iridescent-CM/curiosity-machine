from django.contrib import admin
from .models import *

class FeedbackAdmin(admin.ModelAdmin):
    class Meta:
        model = Feedback

    list_display = ['id', 'challenge_name']
    raw_id_fields = ['challenge']

    def __init__(self, *args, **kwargs):
        fieldsets = (
            (None, {
                'fields': ('challenge', 'is_active', 'question')
            }),
        )

        self.fieldsets = fieldsets
        super().__init__(*args, **kwargs)

    def challenge_name(self, obj):
        return obj.challenge.name

class ResultAdmin(admin.ModelAdmin):
    class Meta:
        model = Result

    list_display = ['id', 'feedback', 'challenge_name', 'user']

    def challenge_name(self, obj):
        return obj.feedback.challenge.name

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Result, ResultAdmin)
