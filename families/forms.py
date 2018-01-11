from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from django.forms import modelform_factory, widgets
from images.models import Image
from locations.models import Location
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import *

LocationModelForm = modelform_factory(
    Location,
    exclude=[],
    widgets={
        "city": widgets.TextInput
    }
)

class FamilyProfileForm(ProfileModelForm):
    class Meta:
        model = FamilyProfile
        fields = ['phone']

    class Media:
        js = ('js/location-form.js',)

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

    phone = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)
    country = LocationModelForm.base_fields['country']
    state = LocationModelForm.base_fields['state']
    city = LocationModelForm.base_fields['city']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('country', None) == 'US':
            if cleaned_data.get('state', None) == None:
                self.add_error(
                    'state',
                    ValidationError(
                        'This field is required',
                        code='required'
                    )
                )
        else:
            cleaned_data['state'] = None
        return cleaned_data

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

    def get_role(self):
        return UserRole.family

    def get_initial(self, user, instance, **kwargs):
        location = {}
        if instance:
            location['country'] = instance.location.country
            location['state'] = instance.location.state
            location['city'] = instance.location.city

        return super().get_initial(
            user,
            instance,
            **location,
            **kwargs
        )

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        exclude = ['image']

    class Media:
        js = ('js/familymember-form.js',)

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

    birthday = forms.DateField(
        required=False,
        widget=forms.extras.SelectDateWidget(
            years=BIRTH_YEAR_CHOICES,
            empty_label=("Year", "Month", "Day"),
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('family_role')
        if role and FamilyRole(role) == FamilyRole.child:
            if not self.cleaned_data.get('birthday'):
                self.add_error(
                    'birthday',
                    ValidationError(
                        'Please set your birthday',
                        code='required'
                    )
                )
        return cleaned_data

    def save(self, commit=False):
        obj = super().save(commit=False)

        if self.cleaned_data.get("image_url"):
            img = Image.from_source_with_job(self.cleaned_data['image_url']['url'])
            obj.image = img

        if commit:
            obj.save()

        return obj

class BaseFamilyMemberFormset(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        if not (
            any(form.cleaned_data['family_role'] == 0 for form in self.forms)
            and any(form.cleaned_data['family_role'] == 1 for form in self.forms)
        ):
            raise forms.ValidationError("You must have at least one parent/guardian and at least one child.")

FamilyMemberFormset = forms.inlineformset_factory(
    get_user_model(),
    FamilyMember,
    form=FamilyMemberForm,
    formset=BaseFamilyMemberFormset,
    exclude=['image'],
    extra=0
)
