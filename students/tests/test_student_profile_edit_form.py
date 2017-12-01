import pytest
from ..factories import *
from ..forms import StudentProfileEditForm

@pytest.mark.django_db
def test_email_gets_put_in_initial():
    user = StudentFactory()
    initial = StudentProfileEditForm(user=user, instance=user.studentprofile).initial
    assert "email" in initial
    assert initial.get("email") == user.email

@pytest.mark.django_db
def test_will_show_user_email_if_allauth_hasnt_synced_yet():
    user = StudentFactory()
    for obj in user.emailaddress_set.all():
        obj.delete()
    initial = StudentProfileEditForm(user=user, instance=user.studentprofile).initial
    assert "email" in initial
    assert initial.get("email") == user.email

@pytest.mark.django_db
def test_changing_email():
    user = StudentFactory()
    data = dict(
        StudentProfileEditForm(user=user, instance=user.studentprofile).initial,
        email="new@mailinator.com"
    )
    form = StudentProfileEditForm(
        user=user,
        instance=user.studentprofile,
        data=data,
    )
    form.save()
    assert user.email == "new@mailinator.com"
    assert user.emailaddress_set.count() == 2
    assert user.emailaddress_set.filter(primary=True).count() == 1
    primary = user.emailaddress_set.filter(primary=True).first()
    assert primary.email == "new@mailinator.com"
    assert primary.primary
    assert not primary.verified