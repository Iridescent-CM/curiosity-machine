import pytest
import mock
from datetime import datetime
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from dateutil.relativedelta import relativedelta
from profiles import forms, models, views, decorators
from profiles.factories import StudentFactory

@pytest.fixture
def parent():
    parent = User(username="parent")
    parent_profile = models.Profile(is_parent=True)
    parent_profile.user = parent
    parent.save()
    parent_profile.user = parent
    parent_profile.save()
    return parent

@pytest.fixture
def child():
    child = User(username="child")
    child_profile = models.Profile(is_student=True, birthday=datetime.now())
    child_profile.user = child
    child.save()
    child_profile.user = child
    child_profile.save()
    return child

@pytest.mark.django_db
def test_gets_ok(client):
    student = StudentFactory(username="student", password="password")
    client.login(username='student', password='password')

    assert client.get('/home/').status_code == 200
    assert client.get('/profile-edit/').status_code == 200
    assert client.get('/underage/').status_code == 200

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

@pytest.mark.django_db
def test_connected_child_only_decorator(rf, parent, child):
    connection = models.ParentConnection.objects.create(child_profile=child.profile, parent_profile=parent.profile)
    request = rf.get('/path')
    view = mock.Mock()
    request.user = parent
    with pytest.raises(PermissionDenied):
        response = decorators.connected_child_only(view)(request, connection_id=connection.id)
        assert not view.called
    request.user = child
    response = decorators.connected_child_only(view)(request, connection_id=connection.id)
    assert view.called
