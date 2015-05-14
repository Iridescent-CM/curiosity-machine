from datetime import date
from django import forms
from profiles.forms.common import UserAndProfileForm

def age(birthday):
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

class StudentUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'birthday',
        'city',
        'parent_first_name',
        'parent_last_name'
    ]
    profile_fields_force = {
        'is_student': True
    }
    make_required = ['city', 'birthday'] # under/over 13 requirement differences enforced in clean()

    form_fields = ['image_url']

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email'
        ]

    def clean(self):
        super(StudentUserAndProfileForm, self).clean()

        birthday = self.cleaned_data.get('birthday')
        if not birthday:
            return self.cleaned_data
        elif age(birthday) < 13:
            return self._clean_underage()
        else:
            return self._clean()

    def _clean_underage(self):
        for fieldname in ['email', 'parent_first_name', 'parent_last_name']:
            if not self.cleaned_data.get(fieldname):
                msg = self.fields[fieldname].error_messages['required']
                self.add_error(fieldname, msg)

        return self.cleaned_data

    def _clean(self):
        return self.cleaned_data