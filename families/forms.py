from allauth.account.adapter import get_adapter
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from images.models import Image
from locations.forms import LocationForm
from operator import itemgetter
from profiles.forms import ProfileModelForm, RelatedModelFormMixin
from profiles.models import UserRole
from .models import *

class FamilyEmailForm(ProfileModelForm):
    class Meta:
        model = FamilyProfile
        fields = []

    def get_role(self):
        return UserRole.family

class FamilyProfileForm(RelatedModelFormMixin, ProfileModelForm):
    related_forms = [
        ('location', LocationForm),
    ]

    class Meta:
        model = FamilyProfile
        fields = []

    class Media:
        js = ('js/location-form.js',)

    image_url = MediaURLField(
        label="Photo",
        mimetypes="image/*",
        widget=FilePickerPickWidget(attrs={
            "data-fp-cropratio": 1,
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_profile = self.user.extra.profile

    def save_related(self, obj):
        obj = super().save_related(obj)

        if self.cleaned_data.get("image_url"):
            img = Image.from_source_with_job(self.cleaned_data['image_url']['url'])
            obj.image = img
        elif self.prev_profile != obj and self.prev_profile.image: # converting to family account scenario
            obj.image = self.prev_profile.image

        return obj

    def get_role(self):
        return UserRole.family

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
            "data-fp-cropratio": 1,
        }),
        required=False
    )

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
            any(form.cleaned_data.get('family_role') == 0 for form in self.forms if not form.cleaned_data.get('DELETE'))
            and any(form.cleaned_data.get('family_role') == 1 for form in self.forms if not form.cleaned_data.get('DELETE'))
        ):
            raise forms.ValidationError("You must have at least one parent/guardian and at least one child.")
        if len([form for form in self.forms if not form.cleaned_data.get('DELETE')]) > 6:
            raise forms.ValidationError("You can have a maximum of 6 family members.")

    def save_user_model_name(self, members, commit=True):
        p_or_gs = self.instance.familymember_set.filter(
            family_role=FamilyRole.parent_or_guardian.value
        ).order_by('id').values('id', 'first_name', 'last_name')
        head = sorted(p_or_gs, key=itemgetter('id'))[0]
        self.instance.first_name = head['first_name']
        self.instance.last_name = head['last_name']
        if commit:
            self.instance.save(update_fields=('first_name', 'last_name'))

    def save(self, commit=True):
        members = super().save(commit=commit)
        self.save_user_model_name(members, commit=commit)
        return members

FamilyMemberFormset = forms.inlineformset_factory(
    get_user_model(),
    FamilyMember,
    form=FamilyMemberForm,
    formset=BaseFamilyMemberFormset,
    exclude=['image'],
    min_num=2,
    max_num=6,
    extra=0
)

class UnusedEmailForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)

        used = AwardForceIntegration.objects.filter(email=value).exists()

        if used:
            raise forms.ValidationError("This e-mail address has already been used to begin a submission.")

        return value

