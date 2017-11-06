from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from datetime import datetime
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from images.models import Image
from profiles.models import UserRole
from .models import StudentProfile

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class NewStudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'birthday',
            'parent_first_name',
            'parent_last_name',
            'city',
        ]

    birthday = forms.DateField(
        widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES),
    )
    parent_first_name = forms.TextInput()
    parent_last_name = forms.TextInput()
    city = forms.TextInput()

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

        obj.user.extra.role = UserRole.student.value
        obj.user.extra.save()

        return obj

class EditStudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = '__all__'