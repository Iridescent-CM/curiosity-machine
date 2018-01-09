from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import *

class EducatorProfileForm(ProfileModelForm):
    class Meta:
        model = EducatorProfile
        fields = [
            'city',
            'organization',
        ]

    city = forms.CharField(required=True)
    organization = forms.CharField(required=True)

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

    def get_initial(self, user, instance):
        return super().get_initial(
            user,
            instance,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    def get_role(self):
        return UserRole.educator

class ImpactSurveyForm(forms.ModelForm):
    class Meta:
        model = ImpactSurvey
        exclude = ('user',)
