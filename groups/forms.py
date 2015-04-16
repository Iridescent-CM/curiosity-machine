from django.contrib.auth.models import User
from django import forms
from . import models
import re

class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ['name']

class GroupJoinForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput, required=True)

class GroupLeaveForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput, required=True)

class GroupInviteForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput, required=True)

class ListField(forms.Field):
    widget = forms.Textarea

    def to_python(self, value):
        if not value:
            return []
        return list(val for val in re.split("[\s;,]+", value) if val)

class MultiInvitationForm(forms.Form):
    recipients = ListField(
        required=True,
        help_text="Enter one or more usernames separated by commas. Usernames are case sensitive."
    )

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        existing = User.objects.filter(
            username__in=recipients,
            profile__is_student=True
        ).values_list('username', flat=True)
        nonexisting = list(set(recipients) - set(existing))
        if nonexisting:
            raise forms.ValidationError(
                "Found no users named: %(users)s",
                code='nonexistant-user',
                params={'users':', '.join(nonexisting)}
            )
        return recipients
