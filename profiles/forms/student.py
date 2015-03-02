from django import forms

class ConsentForm(forms.Form):
    signature = forms.CharField(required=True)