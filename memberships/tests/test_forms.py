import pytest

from memberships.factories import MembershipFactory

from memberships.models import Member
from memberships.forms import RowImportForm

from django.forms.models import modelform_factory
from django.contrib.auth.models import User
from profiles.models import Profile

@pytest.mark.django_db
def test_form_saves_user_and_profile_data():
    membership = MembershipFactory.build()
    f = RowImportForm(
        {
            "username": "username",
            "password": "password",
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
def test_form_reports_user_and_profile_errors():
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
