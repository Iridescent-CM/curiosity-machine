from django import forms
from django.conf import settings

class GroupJoinForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput, required=True)
