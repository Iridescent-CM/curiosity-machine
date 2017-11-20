from django import template
from ..forms import ImpactSurveyForm

register = template.Library()

@register.inclusion_tag('educators/templatetags/impact_survey.html')
def impact_survey():
    return {
        "impact_form": ImpactSurveyForm()
    }

@register.inclusion_tag('educators/templatetags/impact_survey_js.html')
def impact_survey_js():
    return {}
