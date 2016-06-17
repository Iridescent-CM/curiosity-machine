from django import forms
from django.forms.utils import ErrorDict
from django.forms.models import modelform_factory

from memberships.models import Member
from profiles.models import Profile
from django.contrib.auth.models import User

class RowUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if "password" in self.cleaned_data:
            user.set_password(self.cleaned_data["password"])
        return user

class RowImportForm(forms.Form):

    membership = None
    userFormClass = RowUserForm
    profileFormClass = modelform_factory(Profile, fields=['birthday', 'approved'])

    def __init__(self, *args, **kwargs):
        for keyword in list(kwargs.keys()):
            if hasattr(self, keyword):
                setattr(self, keyword, kwargs.pop(keyword))

        return super().__init__(*args, **kwargs)

    def full_clean(self):
        self._errors = ErrorDict()
        self.cleaned_data = {}
        self._forms = []

        for formclass in [self.userFormClass, self.profileFormClass]:
            f = formclass(self.data)
            f.full_clean()
            self._errors.update(f._errors)
            self.cleaned_data.update(f.cleaned_data)
            self._forms.append(f)

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
