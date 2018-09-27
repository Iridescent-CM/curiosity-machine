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

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    def save_related(self, obj):
        if self.cleaned_data.get("image_url"):
            img = Image.from_source_with_job(self.cleaned_data['image_url']['url'])
            obj.image = img

        return obj

    def update_user(self):
        if self.cleaned_data.get('first_name'):
            self.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            self.user.last_name = self.cleaned_data['last_name']

    def get_initial(self, user, instance, **kwargs):
        return super().get_initial(
            user,
            instance,
            first_name=user.first_name,
            last_name=user.last_name,
            **kwargs
        )

    def get_role(self):
        return UserRole.student


class NewStudentProfileForm(StudentProfileEditForm):
    class Meta:
        model = StudentProfile
        fields = [
            'city',
        ]
