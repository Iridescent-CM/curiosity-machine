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

class ManageMembersForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = []

    remove_members = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget = forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super(ManageMembersForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["remove_members"].queryset = self.instance.members()

    def save(self, commit=True):
        if self.cleaned_data['remove_members']:
            removals = models.Membership.objects.filter(
                group=self.instance,
                user__in=self.cleaned_data['remove_members'],
                role=models.Role.member.value
            )
            removals.delete()
        return self.instance

class ManageInvitationsForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = []

    remove_invitations_for = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget = forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super(ManageInvitationsForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["remove_invitations_for"].queryset = self.instance.invited_users

    def save(self, commit=True):
        if self.cleaned_data['remove_invitations_for']:
            invites = models.Invitation.objects.filter(group=self.instance, user__in=self.cleaned_data['remove_invitations_for'])
            invites.delete()
        return self.instance

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
