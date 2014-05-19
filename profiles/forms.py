from django import forms
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime
from curiositymachine.forms import FilePickerURLField

import re

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class ProfileFormBase(forms.Form):
    email = forms.EmailField(max_length=75,required=False, label="Email")
    password = forms.CharField(required=True, max_length=128,
                               widget=forms.PasswordInput(render_value=False), label="Password")
    confirm_password = forms.CharField(required=True, max_length=128,
                                       widget=forms.PasswordInput(render_value=False), label="Retype password")
    first_name = forms.CharField(required=True, label="First Name")
    nickname = forms.CharField(max_length=30, label="Nickname", required=False)
    birthday = forms.DateField(required=True, widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES), label="Date of Birth")
    city = forms.CharField(required=True, label="City")
    picture_filepicker_url = FilePickerURLField(label="Photo", mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)

    def clean(self):
        cleaned_data = super(ProfileFormBase, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if password and len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 characters long')
        return password


class JoinForm(ProfileFormBase):
    username = forms.CharField(max_length=30,required=True, label="Username")
    parent_first_name = forms.CharField(required=True, label="First Name")
    parent_last_name = forms.CharField(required=True, label="Last Name")

    def __init__(self, request=None, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self._request = request

    def clean_username(self):
        username = self.cleaned_data['username']
        if re.match("^[\w.@+-]+$", username) is None:
            raise forms.ValidationError("Username can only include letters, digits and @/./+/-/_")
        return username


class StudentProfileEditForm(ProfileFormBase):
    parent_first_name = forms.CharField(required=True, label="First Name")
    parent_last_name = forms.CharField(required=True, label="Last Name")

    def __init__(self, request, *args, **kwargs):
        super(StudentProfileEditForm, self).__init__(*args, **kwargs)
        self._request = request
        self.user = request.user
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False
        self._initial_values()

    def _initial_values(self):
        self.fields['email'].initial = self.user.email
        self.fields['first_name'].initial = self.user.first_name
        self.fields['nickname'].initial = self.user.profile.nickname
        self.fields['birthday'].initial = self.user.profile.birthday
        self.fields['city'].initial = self.user.profile.city
        self.fields['parent_first_name'].initial = self.user.profile.parent_first_name
        self.fields['parent_last_name'].initial = self.user.profile.parent_last_name

class MentorProfileEditForm(ProfileFormBase):
    title = forms.CharField(required=True, label="What Is My Profession")
    employer = forms.CharField(required=True, label="Where Do I Work?")
    about_me = forms.CharField(required=True, label="About Me")
    about_research = forms.CharField(required=True, label="About My Research")

    def __init__(self, request, *args, **kwargs):
        super(MentorProfileEditForm, self).__init__(*args, **kwargs)
        self._request = request
        self.user = request.user
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False
        self._initial_values()

    def _initial_values(self):
        self.fields['email'].initial = self.user.email
        self.fields['first_name'].initial = self.user.first_name
        self.fields['nickname'].initial = self.user.profile.nickname
        self.fields['birthday'].initial = self.user.profile.birthday
        self.fields['city'].initial = self.user.profile.city
        self.fields['title'].initial = self.user.profile.title
        self.fields['employer'].initial = self.user.profile.employer
        self.fields['about_me'].initial = self.user.profile.about_me
        self.fields['about_research'].initial = self.user.profile.about_research

