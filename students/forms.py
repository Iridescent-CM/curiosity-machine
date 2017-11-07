from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from datetime import datetime, date
from django import forms
from images.models import Image
from profiles.models import UserRole
from .models import StudentProfile

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

# TODO: consolidate this with StudentProfile methods somewhere
def age(birthday):
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

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
        widget=forms.extras.SelectDateWidget(years=BIRTH_YEAR_CHOICES),
    )
    parent_first_name = forms.CharField(required=False)
    parent_last_name = forms.CharField(required=False)
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

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if birthday == date(date.today().year, 1, 1):
            # birthday hasn't been set
            raise forms.ValidationError('Please set your birthday.')
        return birthday

    def clean(self):
        super().clean()

        birthday = self.cleaned_data.get('birthday')
        if not birthday or age(birthday) < 13:
            return self._clean_underage()
        else:
            return self._clean()

    def _clean_underage(self):
        for fieldname in ['parent_first_name', 'parent_last_name']:
            if not self.cleaned_data.get(fieldname):
                msg = self.fields[fieldname].error_messages['required']
                self.add_error(fieldname, msg)

        return self.cleaned_data

    def _clean(self):
        return self.cleaned_data

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

# TODO: build out the actual thing
class EditStudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = '__all__'