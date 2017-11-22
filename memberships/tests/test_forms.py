import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import modelform_factory
from django.utils.timezone import now
from memberships.factories import *
from memberships.forms import RowImportForm
from memberships.models import Member
from profiles.models import UserExtra
from students.models import StudentProfile

User = get_user_model()

def test_row_import_form_requires_fields():
    form = RowImportForm()
    assert form.fields['username'].required
    assert form.fields['password'].required
    assert form.fields['first_name'].required
    assert form.fields['last_name'].required
    assert form.fields['birthday'].required

def test_valid_profile_data_with_default_form():
    examples = [
        {"birthday":"01/01/1990", "approved":"yes"},
    ]

    for example in examples:
        assert RowImportForm.profileFormClass(example).errors.as_data() == {}

def test_extra_approved_values():
    assert RowImportForm.extraFormClass({"approved": "y"}).save(commit=False).approved
    assert RowImportForm.extraFormClass({"approved": "yes"}).save(commit=False).approved
    assert RowImportForm.extraFormClass({"approved": "Y"}).save(commit=False).approved
    assert RowImportForm.extraFormClass({"approved": "YES"}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({"approved": "n"}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({"approved": "no"}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({"approved": "N"}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({"approved": "NO"}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({"approved": ""}).save(commit=False).approved
    assert not RowImportForm.extraFormClass({}).save(commit=False).approved

def test_profile_birthday_values():
    profile = RowImportForm.profileFormClass({"birthday": "01/01/1990"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1/1/90"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1990-01-01"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

def test_extra_has_student_role():
    extra = RowImportForm.extraFormClass({"approved":"yes"}).save(commit=False)
    assert extra.is_student

@pytest.mark.django_db
def test_valid_user_data_with_default_form():
    examples = [{
        "username":"username",
        "password":"password",
        "first_name":"first",
        "last_name":"last",
        "email":"email@example.com"
    }]

    for example in examples:
        assert RowImportForm.userFormClass(example).errors.as_data() == {}

@pytest.mark.django_db
def test_user_password_value_set_as_password():
    user = RowImportForm.userFormClass({
        "username": "username",
        "password": "123123",
        "first_name":"first",
        "last_name":"last",
        "email":"email@example.com"
    }).save()
    assert user.check_password("123123")

@pytest.mark.django_db
def test_case_insensitive_username_duplicates_dont_validate():
    user = RowImportForm.userFormClass({
        "username": "username",
        "password": "123123",
        "first_name": "first",
        "last_name": "last",
        "email":"email@example.com"
    }).save()
    form = RowImportForm.userFormClass({
        "username": "USERNAME",
        "password": "123123",
        "first_name": "first",
        "last_name": "last",
        "email":"email@example.com"
    })
    assert not form.is_valid()
    assert form.errors.as_data()["username"][0].code == 'duplicate'

@pytest.mark.django_db
def test_form_saves_user_and_profile_form_class_data():
    membership = MembershipFactory.build()
    f = RowImportForm(
        {
            "username": "username",
            "city": "cityville",
        },
        membership=membership,
        userFormClass=modelform_factory(User, fields=['username']),
        profileFormClass=modelform_factory(StudentProfile, fields=['city']),
    )
    assert f.is_valid()
    member = f.save(commit=False)

    assert member.user.username == "username"
    assert member.user.studentprofile.city == "cityville"

@pytest.mark.django_db
def test_form_reports_user_and_profile_form_class_errors():
    class ErrorFormOne(forms.Form):
        foo = forms.CharField()

        def clean_foo(self):
            raise forms.ValidationError('nope')

    class ErrorFormTwo(forms.Form):
        bar = forms.CharField()

        def clean_bar(self):
            raise forms.ValidationError('nuh-uh')

    membership = MembershipFactory.build()
    f = RowImportForm(
        {},
        membership=membership,
        userFormClass=ErrorFormOne,
        profileFormClass=ErrorFormTwo,
    )
    assert not f.is_valid()
    assert "foo" in f.errors.keys()
    assert "bar" in f.errors.keys()

@pytest.mark.django_db
def test_saving_form_creates_member_user_and_profile_objects():
    membership = MembershipFactory()
    f = RowImportForm(
        {
            "username": "username",
            "password": "password"
        },
        membership=membership,
        userFormClass=modelform_factory(User, fields=['username']),
        profileFormClass=modelform_factory(StudentProfile, fields=['city']),
        extraFormClass=modelform_factory(UserExtra, fields=['approved']),
    )
    member = f.save()

    assert Member.objects.count() == 1
    assert member == Member.objects.all().first()

    assert member.membership.id == membership.id
    assert member.user
    assert member.user.studentprofile

@pytest.mark.django_db
def test_saving_form_adds_member_to_group():
    membership = MembershipFactory()
    f = RowImportForm(
        {
            "username": "username",
            "password": "password",
            "birthday": "01/01/1990",
            "first_name": "first",
            "last_name": "last",
            "email":"email@example.com",
            "groups": "group 1, group 2"
        },
        membership=membership
    )
    member = f.save()

    assert member.group_set.count() == 2
    assert set(member.group_set.values_list('name', flat=True)) == set(['group 1', 'group 2'])

@pytest.mark.django_db
def test_saving_form_reuses_existing_group():
    membership = MembershipFactory()
    group = GroupFactory(name='group', membership=membership)
    f = RowImportForm(
        {
            "username": "username",
            "password": "password",
            "birthday": "01/01/1990",
            "first_name": "first",
            "last_name": "last",
            "email":"email@example.com",
            "groups": "group"
        },
        membership=membership
    )
    member = f.save()

    assert member.group_set.first() == group
