import pytest
from profiles.factories import *
from ..forms import NewStudentProfileForm

@pytest.mark.django_db
def test_email_gets_put_in_initial():
    user = UserFactory()
    initial = NewStudentProfileForm(user=user).initial
    assert "email" in initial
    assert initial.get("email") == user.email

@pytest.mark.django_db
def test_will_show_user_email_if_allauth_hasnt_synced_yet():
    user = UserFactory()
    for obj in user.emailaddress_set.all():
        obj.delete()
    initial = NewStudentProfileForm(user=user).initial
    assert "email" in initial
    assert initial.get("email") == user.email

@pytest.mark.django_db
def test_form_creates_profile():
    user = UserFactory()
    data = dict(
        NewStudentProfileForm(user=user).initial,
        birthday_month=4,
        birthday_day=12,
        birthday_year=2000,
        city="City",
    )
    form = NewStudentProfileForm(
        user=user,
        data=data,
    )
    assert form.is_valid()
    assert form.save()

@pytest.mark.django_db
def test_form_makes_user_a_student():
    user = UserFactory()
    data = dict(
        NewStudentProfileForm(user=user).initial,
        birthday_month=4,
        birthday_day=12,
        birthday_year=2000,
        city="City",
    )
    form = NewStudentProfileForm(
        user=user,
        data=data,
    )
    form.save()
    assert user.extra.is_student
