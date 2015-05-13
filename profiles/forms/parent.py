from copy import copy
from django import forms
from django.contrib.auth.models import User
from django.forms.models import fields_for_model, model_to_dict
from profiles.models import Profile
from images.models import Image
from curiositymachine.forms import FilePickerDragDropField

class UserAndProfileForm(forms.ModelForm):
    profile_fields = []
    profile_fields_force = {}
    make_required = []

    _form_field_definitions = {
        'image_url': FilePickerDragDropField(
            label="Photo",
            mimetypes="image/*",
            openTo='WEBCAM',
            services='WEBCAM,COMPUTER',
            required=False
        )
    }

    class Meta:
        model = User
        fields = []

        widgets = {
            'password': forms.PasswordInput(render_value=False),
            'city': forms.TextInput
        }

        error_messages = {
            'username': {
                'invalid': "Username can only include letters, digits and @/./+/-/_"
            }
        }

    def __init__(self, *args, **kwargs):
        super(UserAndProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if "password" in self.fields:
            self.fields['confirm_password'] = copy(self.fields['password'])
            self.fields['confirm_password'].label = "Confirm password"

        profile_fields = fields_for_model(
            Profile,
            self.profile_fields,
            [],
            self._meta.widgets,
            None,
            [],
            self._meta.labels,
            self._meta.help_texts,
            self._meta.error_messages
        )
        if instance:
            initial = model_to_dict(instance.profile, self.profile_fields)
            for fieldname, value in initial.items():
                profile_fields.get(fieldname).initial = value
        self.fields.update(profile_fields)

        self.fields.update({key: self._form_field_definitions[key] for key in self.form_fields})

        for fieldname in self.make_required:
            self.fields[fieldname].required = True

        if instance:
            if "password" in self.fields:
                self.fields['password'].required = False
                self.fields['confirm_password'].required = False
            if "username" in self.fields:
                del self.fields['username']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password = password.strip()
            if len(password) < 6:
                raise forms.ValidationError('Password must be at least 6 characters long')
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        if confirm_password:
            confirm_password = confirm_password.strip()
        return confirm_password

    def clean(self):
        super(UserAndProfileForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self.add_error('password', "Passwords do not match.")

        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserAndProfileForm, self).save(commit=False)
        if "password" in self.cleaned_data:
            user.set_password(self.cleaned_data["password"])

        if hasattr(self.instance, "profile"):
            profile = self.instance.profile
        else:
            profile = Profile()
        profile_data = {key: self.cleaned_data[key] for key in self.profile_fields}
        profile_data.update(self.profile_fields_force)
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.user = user

        image = None
        if "image_url" in self.cleaned_data:
            image = Image(source_url=self.cleaned_data['image_url'])
            profile.image = image

        if commit:
            user.save()
            profile.user = user # no user_id otherwise
            if image:
                image.save()
                image.fetch_from_source()
            profile.image = image # no image_id otherwise

            profile.save()

        return user

class ParentUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city'
    ]
    profile_fields_force = {
        'is_parent': True
    }
    make_required = ['email', 'city']

    form_fields = ['image_url']

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        ]
