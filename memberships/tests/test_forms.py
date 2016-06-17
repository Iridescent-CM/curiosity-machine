import pytest

from memberships.factories import MembershipFactory

from memberships.models import Member
from memberships.forms import RowImportForm

from django.forms.models import modelform_factory
from django.contrib.auth.models import User
from profiles.models import Profile

from datetime import date

def test_valid_profile_data_with_default_form():
    examples = [
        {"birthday":"01/01/1990", "approved":"1"},
    ]

    for example in examples:
        assert RowImportForm.profileFormClass(example).errors.as_data() == {}

def test_profile_approved_values():
    profile = RowImportForm.profileFormClass({"approved": "y"}).save(commit=False)
    assert profile.approved

    profile = RowImportForm.profileFormClass({"approved": "1"}).save(commit=False)
    assert profile.approved

    profile = RowImportForm.profileFormClass({"approved": ""}).save(commit=False)
    assert not profile.approved

    profile = RowImportForm.profileFormClass({}).save(commit=False)
    assert not profile.approved

def test_profile_birthday_values():
    profile = RowImportForm.profileFormClass({"birthday": "01/01/1990"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1/1/90"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1990-01-01"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

@pytest.mark.django_db
def test_valid_user_data_with_default_form():
    examples = [
        {"username":"username", "password":"password"},
        {"username":"username", "password":"password", "first_name":"first", "last_name":"last"},
    ]

    for example in examples:
        assert RowImportForm.userFormClass(example).errors.as_data() == {}

@pytest.mark.django_db
def test_user_password_value_set_as_password():
    user = RowImportForm.userFormClass({"username": "username", "password": "123123"}).save()
    assert user.check_password("123123")

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
        profileFormClass=modelform_factory(Profile, fields=['city']),
    )
    assert f.is_valid()
    member = f.save(commit=False)

    assert member.user.username == "username"
    assert member.user.profile.city == "cityville"

@pytest.mark.django_db
def test_form_reports_user_and_profile_form_class_errors():
    membership = MembershipFactory.build()
    f = RowImportForm(
        {
            "username": "user name",
            "gender": "toolong",
        },
        membership=membership,
        userFormClass=modelform_factory(User, fields=['username']),
        profileFormClass=modelform_factory(Profile, fields=['gender']),
    )
    assert not f.is_valid()
    assert "username" in f.errors.keys()
    assert "gender" in f.errors.keys()

@pytest.mark.django_db
def test_saving_form_creates_all_objects():
    membership = MembershipFactory()
    f = RowImportForm(
        {
            "username": "username",
            "password": "password"
        },
        membership=membership,
        userFormClass=modelform_factory(User, fields=['username']),
        profileFormClass=modelform_factory(Profile, fields=['city']),
    )
    member = f.save()

    assert Member.objects.count() == 1
    assert member == Member.objects.all().first()

    assert member.membership.id == membership.id
    assert member.user
    assert member.user.profile

