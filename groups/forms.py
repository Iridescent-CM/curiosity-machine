from django import forms
from django.conf import settings

class GroupForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, required=True)

class GroupJoinForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput, required=True)

class GroupLeaveForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput, required=True)

class GroupInviteForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput, required=True)
