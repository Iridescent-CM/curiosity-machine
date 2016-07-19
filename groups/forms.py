from django.contrib.auth import get_user_model
from django import forms
from curiositymachine.forms import StudentUsernamesField
from . import models

User = get_user_model()

class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ['name']
        help_texts = {
            "name": "This is the group name your students will see."
        }

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
        required=True,
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
        required=True,
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

class MultiInvitationForm(forms.Form):
    recipients = StudentUsernamesField(
        label="Usernames",
        required=True,
        help_text="Enter one or more usernames separated by commas. Usernames are case sensitive."
    )
