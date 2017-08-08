from django import forms
from ..models import ImpactSurvey

class ImpactSurveyForm(forms.ModelForm):
    class Meta:
        model = ImpactSurvey
        exclude = ('user',)

    class Media:
        js = ('foo.js',)
