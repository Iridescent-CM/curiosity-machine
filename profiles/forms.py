from django import forms
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
User = auth.get_user_model()
from datetime import datetime

import re
from cmauth.user_role import Role
from profiles.models import Profile

class JoinForm(forms.Form):
    email = forms.EmailField(max_length=75,required=True, label="Email (User Name)")
    password = forms.CharField(max_length=128,
                               widget=forms.PasswordInput(render_value=False), label="Password")
    confirm_password = forms.CharField(required=True, max_length=128,
                                       widget=forms.PasswordInput(render_value=False), label="Retype password")
    first_name = forms.CharField(required=True, label="First Name", max_length=30)
    nickname = forms.CharField(label="Nickname", max_length=30, required=False)
    birthday = forms.CharField(required=True, max_length=10, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YY'}), label="Date of Birth")
    city = forms.CharField(required=True, label="City", max_length=50)
    parent_first_name = forms.CharField(required=True, label="First Name", max_length=30)
    parent_last_name = forms.CharField(required=True, label="Last Name", max_length=30)


    def __init__(self, request=None, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self._request = request


    def clean(self):
        cleaned_data = super(JoinForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        if not self.errors:
            self.save_user(cleaned_data)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if not email:
            raise forms.ValidationError("This field is required.")
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError("Email has already been used.")

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if not password:
            raise forms.ValidationError("This field is required.")
        if len(password) < 6 or len(password) > 20:
            raise forms.ValidationError('Password must be from 6 to 20 characters long')
        return password

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if re.match("^[0-9][0-9]/[0-9][0-9]/[0-9][0-9]$", birthday) is None:
            raise forms.ValidationError('Birthday needs to be in the form MM/DD/YY')
        return birthday

    def save_user(self, cleaned_data):
        email = cleaned_data['email']
        password = cleaned_data['password']
        first_name = cleaned_data['first_name']
        user = User()
        user.email = email
        user.first_name = first_name
        user.is_active = True
        user.role = Role.STUDENT
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            raise forms.ValidationError('Email has already been used')
        birthday = self.cleaned_data['birthday']
        birthday = datetime.strptime(birthday, "%m/%d/%y").date()
        nickname = self.cleaned_data['nickname']
        city = self.cleaned_data['city']
        parent_first_name = self.cleaned_data['parent_first_name']
        parent_last_name = self.cleaned_data['parent_last_name']
        profile = Profile()
        profile.user = user
        profile.birthday = birthday
        profile.parent_first_name = parent_first_name
        profile.nickname = nickname
        profile.city = city
        profile.parent_first_name = parent_first_name
        profile.parent_last_name = parent_last_name
        profile.save()
        user = auth.authenticate(email=cleaned_data['email'], password=cleaned_data['password'])
        auth.login(self._request, user)
