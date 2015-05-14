import pytest
import mock
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from profiles import forms, models, views

def test_form_required_fields_on_creation_all_ages():
    f = forms.student.StudentUserAndProfileForm()

    required = ['username', 'password', 'confirm_password', 'birthday', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_form_requires_parent_and_email_for_underage():
    bday = now() - relativedelta(years=12)
    f = forms.student.StudentUserAndProfileForm(data={
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert 'parent_first_name' in f.errors
    assert 'parent_last_name' in f.errors
    assert 'email' in f.errors

    bday = now() - relativedelta(years=13, days=1)
    f = forms.student.StudentUserAndProfileForm(data={
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert 'parent_first_name' not in f.errors
    assert 'parent_last_name' not in f.errors
    assert 'email' not in f.errors

def test_form_clean_birthday_set():
    # values are widget initial values
    f = forms.student.StudentUserAndProfileForm(data={
        'birthday_year': now().year,
        'birthday_month': 1,
        'birthday_day': 1
    })
    assert 'birthday' in f.errors

@pytest.mark.django_db
def test_form_sets_is_student_for_all():
    bday = now() - relativedelta(years=13, days=1)
    f = forms.student.StudentUserAndProfileForm(data={
        'username': 'teen',
        'password': '123123',
        'confirm_password': '123123',
        'city': 'mycity',
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert f.is_valid()
    user = f.save()
    assert user.profile.is_student

    bday = now() - relativedelta(years=12)
    f = forms.student.StudentUserAndProfileForm(data={
        'username': 'underage',
        'password': '123123',
        'confirm_password': '123123',
        'city': 'mycity',
        'parent_first_name': 'parent',
        'parent_last_name': 'parent',
        'email': 'parentemail@example.com',
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert f.is_valid()
    user = f.save()
    assert user.profile.is_student

@pytest.mark.django_db
def test_over_13_student_accounts_auto_approve():
    bday = now() - relativedelta(years=13, days=1)
    f = forms.student.StudentUserAndProfileForm(data={
        'username': 'teen',
        'password': '123123',
        'confirm_password': '123123',
        'city': 'mycity',
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert f.is_valid()
    user = f.save()
    assert user.profile.approved

    bday = now() - relativedelta(years=12)
    f = forms.student.StudentUserAndProfileForm(data={
        'username': 'underage',
        'password': '123123',
        'confirm_password': '123123',
        'city': 'mycity',
        'parent_first_name': 'parent',
        'parent_last_name': 'parent',
        'email': 'parentemail@example.com',
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert f.is_valid()
    user = f.save()
    assert not user.profile.approved
