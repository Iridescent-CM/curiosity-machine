from django import forms
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from django.conf import settings
from datetime import datetime
from curiositymachine.forms import FilePickerDragDropField
from datetime import date

import re

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class ProfileFormBase(forms.Form):
    email = forms.EmailField(max_length=75,required=False, label="Email")
    password = forms.CharField(required=True, max_length=128,
                               widget=forms.PasswordInput(render_value=False), label="Password")
    confirm_password = forms.CharField(required=True, max_length=128,
                                       widget=forms.PasswordInput(render_value=False), label="Retype password")
    birthday = forms.DateField(required=True, widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES), label="Date of Birth")
    city = forms.CharField(required=True, label="City")
    picture_filepicker_url = FilePickerDragDropField(label="Photo", mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")

    def clean(self):
        cleaned_data = super(ProfileFormBase, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('password', "Passwords do not match.")
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if password and len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 characters long')
        return password

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if birthday == date(date.today().year, 1, 1):
            # birthday hasn't been set
            raise forms.ValidationError('Please set your birthday.')
        return birthday


def clean_parent_fields(self):
    parent_first_name = self.cleaned_data['parent_first_name']
    parent_last_name = self.cleaned_data['parent_last_name']
    birth_year = int(self.data['birthday_year'])
    birth_month = int(self.data['birthday_month'])
    birth_day = int(self.data['birthday_day'])
    today = date.today()
    age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day)) #subtract a year if birthday hasn't occurred yet
    if age < 13 and not parent_last_name:
        self.add_error('parent_last_name', "This field is required.")
    if age < 13 and not parent_first_name:
        self.add_error('parent_first_name', "This field is required.")

class JoinForm(ProfileFormBase):
    username = forms.CharField(max_length=30,required=True, label="Username")
    parent_first_name = forms.CharField(required=False, label="First Name")
    parent_last_name = forms.CharField(required=False, label="Last Name")


    def __init__(self, request=None, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self._request = request

    def clean(self):
        cleaned_data = super(JoinForm, self).clean()
        clean_parent_fields(self)

    def clean_username(self):
        username = self.cleaned_data['username']
        if re.match("^[\w.@+-]+$", username) is None:
            raise forms.ValidationError("Username can only include letters, digits and @/./+/-/_")
        return username

class MentorJoinForm(ProfileFormBase):
    username = forms.CharField(max_length=30,required=True, label="Username")
    birthday = forms.DateField(required=False, widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES), label="Date of Birth")
    title = forms.CharField(required=False, label="What Is My Profession")
    employer = forms.CharField(required=False, label="Where Do I Work?")

    def __init__(self, request=None, *args, **kwargs):
        super(MentorJoinForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self._request = request

    def clean(self):
        cleaned_data = super(MentorJoinForm, self).clean()

    def clean_username(self):
        username = self.cleaned_data['username']
        if re.match("^[\w.@+-]+$", username) is None:
            raise forms.ValidationError("Username can only include letters, digits and @/./+/-/_")
        return username

    def clean_birthday(self):
        #override the default behaviour that requires the birthday
        return self.cleaned_data['birthday']

class StudentProfileEditForm(ProfileFormBase):
    parent_first_name = forms.CharField(required=False, label="First Name")
    parent_last_name = forms.CharField(required=False, label="Last Name")

    def __init__(self, request, *args, **kwargs):
        super(StudentProfileEditForm, self).__init__(*args, **kwargs)
        self._request = request
        self.user = request.user
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False
        self._initial_values()

    def clean(self):
        cleaned_data = super(StudentProfileEditForm, self).clean()
        clean_parent_fields(self)

    def _initial_values(self):
        self.fields['email'].initial = self.user.email
        self.fields['birthday'].initial = self.user.profile.birthday
        self.fields['city'].initial = self.user.profile.city
        self.fields['parent_first_name'].initial = self.user.profile.parent_first_name
        self.fields['parent_last_name'].initial = self.user.profile.parent_last_name

class MentorProfileEditForm(ProfileFormBase):
    title = forms.CharField(required=False, label="What Is My Profession")
    employer = forms.CharField(required=False, label="Where Do I Work?")
    expertise = forms.CharField(required=False, label="Expertise In", widget=forms.Textarea)
    birthday = forms.DateField(required=False, widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES), label="Date of Birth")
    about_me = forms.CharField(required=False, label="About Me")
    about_me_filepicker_mimetype_widget = forms.HiddenInput(attrs={"id":"about_me_mimetype"})
    about_me_filepicker_url = FilePickerDragDropField(
        label="About Me Photo or Video",
        mimetypes="video/*,image/*",
        openTo='WEBCAM',
        services='VIDEO,WEBCAM,COMPUTER',
        required=False,
        mimetype_widget=about_me_filepicker_mimetype_widget
    )
    about_me_filepicker_mimetype = forms.CharField(
        required=False, 
        widget=about_me_filepicker_mimetype_widget
    )

    about_research = forms.CharField(required=False, label="About My Research")
    about_research_filepicker_mimetype_widget = forms.HiddenInput(attrs={"id":"about_research_mimetype"})
    about_research_filepicker_url = FilePickerDragDropField(
        label="About My Research Photo or Video",
        mimetypes="video/*,image/*",
        openTo='WEBCAM',
        services='VIDEO,WEBCAM,COMPUTER',
        required=False,
        mimetype_widget=about_research_filepicker_mimetype_widget
    )
    about_research_filepicker_mimetype = forms.CharField(
        required=False, 
        widget=about_research_filepicker_mimetype_widget
    )

    def __init__(self, request, *args, **kwargs):
        super(MentorProfileEditForm, self).__init__(*args, **kwargs)
        self._request = request
        self.user = request.user
        self.fields['email'].required = True
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False
        self._initial_values()

    def _initial_values(self):
        self.fields['email'].initial = self.user.email
        self.fields['birthday'].initial = self.user.profile.birthday
        self.fields['city'].initial = self.user.profile.city
        self.fields['title'].initial = self.user.profile.title
        self.fields['employer'].initial = self.user.profile.employer
        self.fields['about_me'].initial = self.user.profile.about_me
        self.fields['about_research'].initial = self.user.profile.about_research

