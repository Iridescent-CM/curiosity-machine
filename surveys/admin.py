from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from .models import *
from .updating import Updating

class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey_id', 'user', 'status', 'created_at', 'updated_at']
    list_filter = [('status', EnumFieldListFilter)]
    readonly_fields = ['id', 'survey_id', 'user', 'created_at', 'updated_at']
    search_fields = ['id', 'survey_id', 'user__username']

    def save_model(self, request, obj, form, change):
        if not change:
            return super().save_model(request, obj, form, change)

        if form.has_changed():
            # it can only be status because of readonly_fields above
            Updating(obj, form.cleaned_data['status']).run()

admin.site.register(SurveyResponse, SurveyResponseAdmin)
