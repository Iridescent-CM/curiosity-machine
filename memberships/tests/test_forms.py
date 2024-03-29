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
from students.factories import *

User = get_user_model()

def test_row_import_form_requires_fields():
    form = RowImportForm()
    assert form.fields['username'].required
    assert form.fields['password'].required
    assert form.fields['first_name'].required
    assert form.fields['last_name'].required
    assert form.fields['approved'].required

@pytest.mark.django_db
def test_valid_data_has_no_error():
    assert RowImportForm(CSVRowDataFactory()).errors.as_data() == {}
    assert RowImportForm(CSVRowDataFactory(approved="y")).errors.as_data() == {}

@pytest.mark.django_db
def test_form_saves_expected_user():
    membership = MembershipFactory.build()
    data = CSVRowDataFactory(
        approved="y",
    )
    f = RowImportForm(
        data,
        membership=membership
    )
    assert f.is_valid()
    member = f.save(commit=False)

    for attr in ['username', 'first_name', 'last_name', 'email']:
        assert getattr(member.user, attr) == data[attr] 
    assert member.user.studentprofile.full_access

@pytest.mark.django_db
def test_approved_values():
    def approves(**kwargs):
        return RowImportForm(CSVRowDataFactory(**kwargs)).save(commit=False).user.studentprofile.full_access

    assert approves(approved="y")
    assert approves(approved="yes")
    assert approves(approved="Y")
    assert approves(approved="YES")
    assert not approves(approved="n")
    assert not approves(approved="no")
    assert not approves(approved="N")
    assert not approves(approved="NO")
    assert not approves(approved="")
    assert not approves()

@pytest.mark.django_db
def test_has_student_role():
    obj = RowImportForm(CSVRowDataFactory(), membership=MembershipFactory()).save(commit=False)
    assert obj.user.extra.is_student

@pytest.mark.django_db
def test_user_password_value_set_as_password():
    user = RowImportForm(
        CSVRowDataFactory(password="123123"),
        membership=MembershipFactory()
    ).save().user
    assert user.check_password("123123")

@pytest.mark.django_db
def test_case_insensitive_username_duplicates_dont_validate():
    user = RowImportForm(
        CSVRowDataFactory(username="username"),
        membership=MembershipFactory()
    ).save()
    form = RowImportForm(
        CSVRowDataFactory(username="USERNAME"),
        membership=MembershipFactory()
    )
    assert not form.is_valid()
    assert form.errors.as_data()["username"][0].code == 'duplicate'

@pytest.mark.django_db
def test_saving_form_adds_member_to_group():
    membership = MembershipFactory()
    f = RowImportForm(
        {
            "username": "username",
            "password": "password",
            "first_name": "first",
            "last_name": "last",
            "email":"email@example.com",
            "groups": "group 1, group 2",
            "approved": "yes"
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
            "first_name": "first",
            "last_name": "last",
            "email":"email@example.com",
            "groups": "group",
            "approved": "yes"
        },
        membership=membership
    )
    member = f.save()

    assert member.group_set.first() == group
