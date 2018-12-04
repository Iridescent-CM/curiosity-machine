from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from . import get_survey
from .models import *
from .updating import Updating

class SurveyNameFilter(admin.SimpleListFilter):
    title = "Name"
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        ids = SurveyResponse.objects.distinct('survey_id').values_list('survey_id', flat=True)
        return ((id, "%s - %s" % (id, getattr(get_survey(id), "name", "n/a"))) for id in ids)

    def queryset(self, request, queryset):
        return queryset.filter(survey_id=self.value())

class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey_id', 'user', 'status', 'created_at', 'updated_at']
    list_filter = [('status', EnumFieldListFilter), SurveyNameFilter]
    readonly_fields = ['id', 'survey_id', 'user', 'created_at', 'updated_at']
    search_fields = ['id', 'survey_id', 'user__username']
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if not change:
            return super().save_model(request, obj, form, change)

        if form.has_changed():
            # it can only be status because of readonly_fields above,
            # Updating wants the original, not the modified (FIXME?)
            Updating(SurveyResponse.objects.get(pk=obj.id), form.cleaned_data['status']).run()

admin.site.register(SurveyResponse, SurveyResponseAdmin)
