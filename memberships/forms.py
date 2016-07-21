from django import forms
from django.forms.utils import ErrorDict
from django.forms.models import modelform_factory
from collections import OrderedDict

from memberships.models import Member
from profiles.models import Profile, UserRole
from django.contrib.auth.models import User

class RowUserForm(forms.ModelForm):
    """
    Validates user fields and builds user object from a csv row
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

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
        model = Profile
        fields = ['birthday', 'approved']

    def save(self, commit=False):
        profile = super().save(commit=False)
        profile.role = UserRole.student.value
        if commit:
            profile.save()
        return profile


class RowImportForm(forms.Form):
    """
    Provides a single ModelForm-ish facade on top of User and Profile forms
    to build connected User, Profile, and Member objects from csv row
    """
    membership = None
    userFormClass = RowUserForm
    profileFormClass = RowProfileForm

    def __init__(self, data=None, *args, **kwargs):
        for keyword in list(kwargs.keys()):
            if hasattr(self, keyword):
                setattr(self, keyword, kwargs.pop(keyword))

        self._forms = []
        for formclass in [self.userFormClass, self.profileFormClass]:
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

        userForm, profileForm = self._forms
        profile = profileForm.save(commit=False)
        user = userForm.save(commit=False)
        user.profile = profile
        member = Member(membership=self.membership, user=user)

        if commit:
            user.save()
            user.profile = profile
            profile.save()
            member.user = user
            member.save()

        return member
