from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from locations.forms import LocationForm
from memberships.models import Member
from profiles.forms import ProfileModelForm, RelatedModelFormMixin
from profiles.models import UserRole
from .models import *

class EducatorProfileForm(RelatedModelFormMixin, ProfileModelForm):
    related_forms = [
        ('location', LocationForm),
    ]

    class Meta:
        model = EducatorProfile
        fields = [
            'organization',
            'title_i',
        ]

    class Media:
        js = ('js/location-form.js',)

    organization = forms.CharField(required=True, label="Organization name")
    title_i = forms.ChoiceField(
        label="Organization is a Title I or underserved school?",
        choices=((True, "Yes"), (False, "No")),
        initial=False,
        widget=forms.RadioSelect,
    )

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

    coach_signup = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def save_related(self, obj):
        obj = super().save_related(obj)

        if self.cleaned_data.get("image_url"):
            img = Image.from_source_with_job(self.cleaned_data['image_url']['url'])
            obj.image = img

        if self.cleaned_data.get("coach_signup"):
            Member.objects.get_or_create(user=self.user, membership_id=settings.AICHALLENGE_COACH_MEMBERSHIP_ID)

        return obj

    def update_user(self):
        if self.cleaned_data.get('first_name'):
            self.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            self.user.last_name = self.cleaned_data['last_name']

    def get_initial(self, user, instance):
        location = {}
        if instance and not instance.location and instance.city:
            location['city'] = instance.city

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
