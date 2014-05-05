from django import forms
from django.forms.extras.widgets import SelectDateWidget

class AnalyticsForm(forms.Form):
    start_date = forms.DateField(widget=SelectDateWidget())
    end_date = forms.DateField(widget=SelectDateWidget())