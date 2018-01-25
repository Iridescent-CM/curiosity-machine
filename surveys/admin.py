from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from .models import *

class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey_id', 'user', 'status', 'created_at', 'updated_at']
    list_filter = [('status', EnumFieldListFilter)]
    readonly_fields = ['id', 'survey_id', 'user', 'created_at', 'updated_at']
    search_fields = ['id', 'survey_id', 'user__username']

admin.site.register(SurveyResponse, SurveyResponseAdmin)
