from django.contrib import admin
from .models import *

class ImpactSurveyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'student_count',
        'teacher_count',
        'challenge_count',
        'hours_per_challenge',
        'in_classroom',
        'out_of_classroom',
        'created_at',
    )
    raw_id_fields = ('user',)
    readonly_fields = (
        'id',
        'user',
        'student_count',
        'teacher_count',
        'challenge_count',
        'hours_per_challenge',
        'in_classroom',
        'out_of_classroom',
        'comment',
        'created_at',
    )

admin.site.register(ImpactSurvey, ImpactSurveyAdmin)
