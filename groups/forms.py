from django import forms
from . import models

class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ('name',)

class GroupJoinForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput, required=True)

class GroupLeaveForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput, required=True)

class GroupInviteForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput, required=True)
