import re
from collections import OrderedDict
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms.models import modelform_factory
from django.forms.utils import ErrorDict
from memberships.models import Member, Group, GroupMember
from profiles.models import UserRole, UserExtra
from students.models import StudentProfile

User = get_user_model()

class YesNoBooleanField(forms.BooleanField):
    """
    Converts case-insensitive yes, no, y, n, or blank text input value to boolean
    """

    widget = forms.TextInput

    def to_python(self, value):
        if value is None:
            return False

        if re.match('^(yes|y|no|n)?$', value, flags=re.IGNORECASE) is None:
            raise ValidationError('Valid values are yes/y or no/n', code='invalid')

        if value.lower() in ('y', 'yes'):
            return True

        return False

class RowUserForm(forms.ModelForm):
    """
    Validates user fields and builds user object from a csv row
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.', code='duplicate')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if "password" in self.cleaned_data:
            user.set_password(self.cleaned_data["password"])
        user.skip_welcome_email = True
        user.skip_mailing_list_subscription = True
        if commit:
            user.save()
        return user

class RowProfileForm(forms.ModelForm):
    """
    Validates profile fields and builds object from a csv row
    """
    class Meta:
        model = StudentProfile
        fields = ['birthday']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birthday'].required = True

class RowUserExtraForm(forms.ModelForm):
    """
    Validates extra fields and builds object from a csv row
    """
    class Meta:
        model = UserExtra
        fields = ['approved']

    approved = YesNoBooleanField(required=False, label='Consent form')

    def save(self, commit=False):
        obj = super().save(commit=False)
        obj.role = UserRole.student.value
        if commit:
            obj.save()
        return obj

class RowGroupsForm(forms.Form):
    """
    Collects group name(s) for user in a csv row
    """
    groups = forms.CharField(required=False, label='Groups')

class RowImportForm(forms.Form):
    """
    Provides a single ModelForm-ish facade on top of User, Profile, and Group forms
    to build connected User, Profile, Member, Group, and GroupMember objects from csv row
    """
    membership = None
    userFormClass = RowUserForm
    profileFormClass = RowProfileForm
    extraFormClass = RowUserExtraForm
    groupFormClass = RowGroupsForm

    def __init__(self, data=None, *args, **kwargs):
        for keyword in list(kwargs.keys()):
            if hasattr(self, keyword):
                setattr(self, keyword, kwargs.pop(keyword))

        self._forms = []
        for formclass in [self.userFormClass, self.profileFormClass, self.extraFormClass, self.groupFormClass]:
            self._forms.append(formclass(data))

        return super().__init__(data, *args, **kwargs)

    @property
    def fields(self):
        fields = OrderedDict()
        for form in self._forms:
            fields.update(form.fields.copy())
        return fields

    @fields.setter
    def fields(self, value):
        pass
        # fields are always derived from our wrapped forms

    def full_clean(self):
        self._errors = ErrorDict()
        self.cleaned_data = {}

        for form in self._forms:
            form.full_clean()
            self._errors.update(form._errors)
            self.cleaned_data.update(form.cleaned_data)

    def save(self, commit=True):
        if self.errors:
            raise ValueError("RowImportForm cannot save because data did not validate")

        cleaned_data = self.cleaned_data

        userForm, profileForm, extraForm, groupForm = self._forms
        profile = profileForm.save(commit=False)
        extra = extraForm.save(commit=False)
        user = userForm.save(commit=False)
        user.studentprofile = profile
        user.extra = extra
        member = Member(membership=self.membership, user=user)

        groups = []
        names = []
        if cleaned_data['groups']:
            names = [s.strip() for s in cleaned_data['groups'].split(',')]
        for name in names:
            group = Group(membership=self.membership, name=name)
            groupmember = GroupMember(group=group, member=member)
            groups.append((group, groupmember))

        if commit:
            user.save()
            user.extra = extra
            extra.save()
            user.studentprofile = profile
            profile.save()
            member.user = user
            member.save()

            for group, groupmember in groups:
                group, created = Group.objects.get_or_create(membership=group.membership, name=group.name)
                groupmember.group = group
                groupmember.member = member
                groupmember.save()

        return member
