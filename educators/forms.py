from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from locations.forms import LocationForm
from locations.models import Location
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import *

class EducatorProfileForm(ProfileModelForm):
    class Meta:
        model = EducatorProfile
        fields = [
            'organization',
        ]

    class Media:
        js = ('js/location-form.js',)

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

    country = LocationForm.base_fields['country']
    state = LocationForm.base_fields['state']
    city = LocationForm.base_fields['city']

    def clean(self):
        cleaned_data = super().clean()
        return self.proxy_clean(cleaned_data, LocationForm)

    def save_related(self, obj):
        location, created = Location.objects.get_or_create(
            country=self.cleaned_data['country'],
            state=self.cleaned_data['state'],
            city=self.cleaned_data['city']
        )
        obj.location = location

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
        location = {}
        if instance and instance.location:
            location['country'] = instance.location.country
            location['state'] = instance.location.state
            location['city'] = instance.location.city

        return super().get_initial(
            user,
            instance,
            first_name=user.first_name,
            last_name=user.last_name,
            **location,
        )

    def get_role(self):
        return UserRole.educator

class ImpactSurveyForm(forms.ModelForm):
    class Meta:
        model = ImpactSurvey
        exclude = ('user',)
