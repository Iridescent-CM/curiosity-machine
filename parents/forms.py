from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from profiles.models import UserRole
from .models import *

class NewParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = [
            'city',
        ]

    city = forms.CharField(required=False)

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

    def save(self, commit=True):
        if not commit:
            # Save without commit is weird since so many related models are updated
            raise NotImplementedError("Save without commit not yet implemented.")

        user = self.initial.get('user')
        if not user:
            raise NotImplementedError("Save cannot be called unless User provided in form initials.")

        obj = super().save(commit=False)
        obj.user = user

        if self.cleaned_data.get("image_url"):
            img = Image(source_url=self.cleaned_data['image_url']['url'])
            img.save()
            obj.image = img

        obj.save()

        obj.user.extra.role = UserRole.parent.value
        obj.user.extra.save()

        return obj

class EditStudentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = '__all__'
