from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from profiles.models import Profile
from images.models import Image
from curiositymachine.forms import FilePickerDragDropField


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(
        required=True,
        max_length=128,
        widget=forms.PasswordInput(render_value=False),
        label="Password"
    )
    confirm_password = forms.CharField(
        required=True,
        max_length=128,
        widget=forms.PasswordInput(render_value=False),
        label="Retype password"
    )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

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
        super(UserCreationForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('password', "Passwords do not match.")

        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name'
        ]


class UserChangeForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        max_length=128,
        widget=forms.PasswordInput(render_value=False),
        label="Password"
    )
    confirm_password = forms.CharField(
        required=False,
        max_length=128,
        widget=forms.PasswordInput(render_value=False),
        label="Retype password"
    )

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
        super(UserChangeForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self.add_error('password', "Passwords do not match.")

        return self.cleaned_data

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name'
        ]

class ProfileChangeForm(forms.ModelForm):
    image_url = FilePickerDragDropField(
        label="Photo",
        mimetypes="image/*",
        openTo='WEBCAM',
        services='WEBCAM,COMPUTER',
        required=False
    )

    def clean_is_educator(self):
        return True

    def clean_is_student(self):
        return False

    def clean_is_mentor(self):
        return False

    def clean(self):
        super(ProfileChangeForm, self).clean()

        self.stached_data = {}
        if 'image_url' in self.cleaned_data:
            self.stached_data['image_url'] = self.cleaned_data['image_url']
            del self.cleaned_data['image_url']

        return self.cleaned_data

    def save(self, commit=True):
        profile = super(ProfileChangeForm, self).save(commit=False)

        if 'image_url' in self.stached_data:
            image = Image(source_url=self.stached_data['image_url'])
            if commit: 
                image.save()
                image.fetch_from_source()
            profile.image = image

        if commit:
            profile.save()

        return profile

    class Meta:
        model = Profile
        fields = ['image', 'is_educator']
