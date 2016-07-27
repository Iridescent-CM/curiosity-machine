import pytest

from memberships.factories import MembershipFactory

from memberships.models import Member
from memberships.forms import RowImportForm

from django.forms.models import modelform_factory
from django.contrib.auth import get_user_model
from profiles.models import Profile

from datetime import date
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

def test_row_import_form_requires_fields():
    form = RowImportForm()
    assert form.fields['username'].required
    assert form.fields['password'].required
    assert form.fields['first_name'].required
    assert form.fields['last_name'].required
    assert form.fields['birthday'].required

def test_row_import_form_normalizes_fancy_fieldnames():
    form = RowImportForm({
        " Username ": "user",
        " Pass Word ": "123123",
    })
    assert form.data == {
        "username": "user",
        "pass_word": "123123",
    }

def test_row_import_form_maps_fieldnames():
    form = RowImportForm(
        {
            " User Name ": "user",
        },
        fieldname_mappings={"user_name": "whatever"}
    )
    assert form.data == {
        "whatever": "user",
    }

User = get_user_model()

def test_valid_profile_data_with_default_form():
    examples = [
        {"birthday":"01/01/1990", "approved":"yes"},
    ]

    for example in examples:
        assert RowImportForm.profileFormClass(example).errors.as_data() == {}

def test_profile_approved_values():
    birthday = now() - relativedelta(years=5)
    birthday = birthday.strftime('%m/%d/%Y')
    assert RowImportForm.profileFormClass({"approved": "y", "birthday": birthday}).save(commit=False).approved
    assert RowImportForm.profileFormClass({"approved": "yes", "birthday": birthday}).save(commit=False).approved
    assert RowImportForm.profileFormClass({"approved": "Y", "birthday": birthday}).save(commit=False).approved
    assert RowImportForm.profileFormClass({"approved": "YES", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"approved": "n", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"approved": "no", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"approved": "N", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"approved": "NO", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"approved": "", "birthday": birthday}).save(commit=False).approved
    assert not RowImportForm.profileFormClass({"birthday": birthday}).save(commit=False).approved

def test_profile_birthday_values():
    profile = RowImportForm.profileFormClass({"birthday": "01/01/1990"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1/1/90"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

    profile = RowImportForm.profileFormClass({"birthday": "1990-01-01"}).save(commit=False)
    assert profile.birthday == date(month=1, day=1, year=1990)

def test_profile_has_student_role():
    profile = RowImportForm.profileFormClass({"birthday":"01/01/1990", "approved":"yes"}).save(commit=False)
    assert profile.is_student

@pytest.mark.django_db
def test_valid_user_data_with_default_form():
    examples = [
        {"username":"username", "password":"password", "first_name":"first", "last_name":"last"},
    ]

    for example in examples:
        assert RowImportForm.userFormClass(example).errors.as_data() == {}

@pytest.mark.django_db
def test_user_password_value_set_as_password():
    user = RowImportForm.userFormClass({"username": "username", "password": "123123", "first_name":"first", "last_name":"last"}).save()
    assert user.check_password("123123")

@pytest.mark.django_db
def test_case_insensitive_username_duplicates_dont_validate():
    user = RowImportForm.userFormClass({"username": "username", "password": "123123", "first_name": "first", "last_name": "last"}).save()
    form = RowImportForm.userFormClass({"username": "USERNAME", "password": "123123", "first_name": "first", "last_name": "last"})
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
