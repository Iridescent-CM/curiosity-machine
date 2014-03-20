from django import forms
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from datetime import datetime

import re

class JoinForm(forms.Form):
    username = forms.CharField(max_length=254,required=True, label="Username")
    email = forms.EmailField(max_length=254,required=False, label="Email")
    password = forms.CharField(max_length=128,
                               widget=forms.PasswordInput(render_value=False), label="Password")
    confirm_password = forms.CharField(required=True, max_length=128,
                                       widget=forms.PasswordInput(render_value=False), label="Retype password")
    first_name = forms.CharField(required=True, label="First Name")
    nickname = forms.CharField(label="Nickname", required=False)
    birthday = forms.CharField(required=True, max_length=8, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YY'}), label="Date of Birth")
    city = forms.CharField(required=True, label="City")
    parent_first_name = forms.CharField(required=True, label="First Name")
    parent_last_name = forms.CharField(required=True, label="Last Name")


    def __init__(self, request=None, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self._request = request


    def clean(self):
        cleaned_data = super(JoinForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return email

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if not password:
            raise forms.ValidationError("This field is required.")
        if len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 characters long')
        return password

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        try:
            birthday = datetime.strptime(birthday, "%m/%d/%y").date()
        except ValueError:
            raise forms.ValidationError('Birthday needs to be in the form MM/DD/YY')
        return birthday

