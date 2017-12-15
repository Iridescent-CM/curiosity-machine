from curiositymachine.forms import MediaURLField, StudentUsernamesField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from django.db.models import F
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import *

class ParentProfileForm(ProfileModelForm):
    class Meta:
        model = ParentProfile
        fields = [
            'city',
        ]

    city = forms.CharField(required=True)

    image_url = MediaURLField(
        label="Photo",
        mimetypes="image/*",
        widget=FilePickerPickWidget(attrs={
            "data-fp-opento": "WEBCAM",
            "data-fp-services": "WEBCAM,COMPUTER,CONVERT",
            "data-fp-conversions": "crop,rotate",
            "data-fp-cropratio": 1,
            "data-fp-cropforce": "force",
        }),
        required=False
    )

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def save_related(self, obj):
        if self.cleaned_data.get("image_url"):
            img = Image(source_url=self.cleaned_data['image_url']['url'])
            img.save()
            obj.image = img
        return obj

    def update_user(self):
        if self.cleaned_data.get('first_name'):
            self.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            self.user.last_name = self.cleaned_data['last_name']

    def get_initial_from_user(self, user, **kwargs):
        return super().get_initial_from_user(user,
            first_name=user.first_name,
            last_name=user.last_name,
            **kwargs
        )

    def get_role(self):
        return UserRole.parent

class ConnectForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = []

    usernames = StudentUsernamesField(
        required=True,
        help_text="Enter one or more usernames separated by commas. Usernames are case sensitive."
    )

    def save(self, commit=True):
        profiles = StudentProfile.objects.filter(user__username__in=self.cleaned_data["usernames"])
        for profile in profiles:
            updated = ParentConnection.objects.filter(
                parent_profile=self.instance,
                child_profile=profile,
            ).update(
                removed=False,
                active=False,
                retries=F("retries") + 1
            )
            if updated == 0:
                ParentConnection.objects.create(
                    parent_profile=self.instance,
                    child_profile=profile,
                    removed=False,
                    active=False,
                    retries=0
                )
        return self.instance
