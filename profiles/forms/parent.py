from django import forms
from profiles.forms.common import UserAndProfileForm
from profiles.models import ParentConnection, Profile
from curiositymachine.forms import StudentUsernamesField

class ParentUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city'
    ]
    profile_fields_force = {
        'is_parent': True
    }
    make_required = ['email', 'city']

    form_fields = ['image_url']

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        ]

class ConnectForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = []

    usernames = StudentUsernamesField(
        required=True,
        help_text="Enter one or more usernames separated by commas. Usernames are case sensitive."
    )

    def save(self, commit=True):
        profiles = Profile.objects.filter(user__username__in=self.cleaned_data["usernames"])
        for profile in profiles:
            ParentConnection.objects.update_or_create(
                parent_profile=self.instance,
                child_profile=profile,
                defaults={
                    "removed": False,
                    "active": False
                }
            )
        return self.instance
