import re
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms.models import modelform_factory
from django.forms.utils import ErrorDict
from django.utils.timezone import now
from memberships.models import Member, Group, GroupMember
from profiles.models import UserRole, UserExtra
from students.models import StudentProfile

User = get_user_model()

class YesNoBooleanField(forms.NullBooleanField):
    """
    Converts case-insensitive yes, no, y, n, or blank text input value to boolean
    """

    widget = forms.TextInput

    def to_python(self, value):
        if not value:
            return None

        if re.match('^(yes|y|no|n)?$', value, flags=re.IGNORECASE) is None:
            raise ValidationError('Valid values are yes/y or no/n', code='invalid')

        if value.lower() in ('y', 'yes'):
            return True

        return False

class RowImportForm(forms.Form):
    username = User._meta.get_field('username').formfield(required=True)
    password = User._meta.get_field('password').formfield(required=True)
    first_name = User._meta.get_field('first_name').formfield(required=True)
    last_name = User._meta.get_field('last_name').formfield(required=True)
    email = User._meta.get_field('email').formfield(required=True)
    groups = forms.CharField(required=False, label='Groups')
    approved = YesNoBooleanField(required=True, label='Consent form')

    def __init__(self, *args, **kwargs):
        self.membership = kwargs.pop('membership', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.', code='duplicate')
        return username

    def save(self, commit=True):
        if self.errors:
            raise ValueError("RowImportForm cannot save because data did not validate")

        cleaned_data = self.cleaned_data

        profile = StudentProfile()
        profile.full_access = cleaned_data['approved'] 
        extra = UserExtra()
        extra.role = UserRole.student.value
        user = User(**{k: cleaned_data[k] for k in ['username', 'first_name', 'last_name', 'email']})
        user.set_password(self.cleaned_data['password'])
        user.skip_welcome_email = True
        user.skip_mailing_list_subscription = True
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
