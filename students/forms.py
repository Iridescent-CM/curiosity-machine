from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from datetime import datetime, date
from django import forms
from images.models import Image
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import StudentProfile

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class StudentProfileEditForm(ProfileModelForm):
    class Meta:
        model = StudentProfile
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

    def save_related(self, obj):
        if self.cleaned_data.get("image_url"):
            img = Image(source_url=self.cleaned_data['image_url']['url'])
            img.save()
            obj.image = img

        return obj

    def get_role(self):
        return UserRole.student


class NewStudentProfileForm(StudentProfileEditForm):
    class Meta:
        model = StudentProfile
        fields = [
            'birthday',
            'city',
        ]

    birthday = forms.DateField(
        required=False,
        widget=forms.extras.SelectDateWidget(
            years=BIRTH_YEAR_CHOICES,
            empty_label=("Year", "Month", "Day"),
        ),
    )

    def clean_birthday(self):
        if not self.cleaned_data.get('birthday'):
            raise forms.ValidationError('Please set your birthday.')
        return self.cleaned_data.get('birthday')
