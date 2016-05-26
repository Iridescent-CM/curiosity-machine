import pytest
import mock
from datetime import datetime
from profiles import forms, models, decorators
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied

@pytest.fixture
def parent():
    parent = User(username="parent")
    parent_profile = models.Profile(role=models.UserRole.parent.value)
    parent_profile.user = parent
    parent.save()
    parent_profile.user = parent
    parent_profile.save()
    return parent

@pytest.fixture
def child():
    child = User(username="child")
    child_profile = models.Profile(role=models.UserRole.student.value, birthday=datetime.now())
    child_profile.user = child
    child.save()
    child_profile.user = child
    child_profile.save()
    return child

def test_form_required_fields_on_creation():
    f = forms.parent.ParentUserAndProfileForm()

    required = ['username', 'email', 'password', 'confirm_password', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_form_required_fields_on_edit():
    user = User()
    profile = models.Profile()
    profile.user = user
    f = forms.parent.ParentUserAndProfileForm(instance=user)

    required = ['email', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

@pytest.mark.django_db
def test_creates_user_with_profile():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    assert f.is_valid()
    user = f.save()
    assert hasattr(user, "profile")
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

@pytest.mark.django_db
def test_modifies_exisiting_user_and_profile():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity',
    })
    user = f.save()
    f = forms.parent.ParentUserAndProfileForm(
        instance=user,
        data={
            'email': 'new@example.com',
            'city': 'newcity'
        }
    )
    user = f.save()
    assert user.email == 'new@example.com'
    assert user.profile.city == 'newcity'
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

@pytest.mark.django_db
def test_sets_parent_role():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    user = f.save()
    assert user.profile.is_parent

@pytest.mark.django_db
def test_form_ignores_unspecified_profile_fields():
    f = forms.parent.ParentUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity',
        'role': models.UserRole.student.value,
        'title': 'title'
    })
    user = f.save()
    assert not user.profile.is_student
    assert user.profile.title == ''

def test_connect_form_requires_usernames():
    form = forms.parent.ConnectForm(data={})
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'required'

@pytest.mark.django_db
def test_connect_form_validates_existance():
    form = forms.parent.ConnectForm(data={
        "usernames": "nope"
    })
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'nonexistant-user'

@pytest.mark.django_db
def test_connect_form_connects_to_usernames(parent, child):
    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    assert form.is_valid()
    assert models.ParentConnection.objects.all().count() == 0
    form.save()
    assert models.ParentConnection.objects.all().count() == 1
    assert [profile.id for profile in parent.profile.child_profiles.all()] == [child.profile.id]

@pytest.mark.django_db
def test_connect_form_reuses_and_resets_parentconnection_objects(parent, child):
    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    conn = models.ParentConnection.objects.all().first()
    conn.active = True
    conn.removed = True
    conn.save()
    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert models.ParentConnection.objects.all().count() == 1
    assert models.ParentConnection.objects.all().first().removed == False
    assert models.ParentConnection.objects.all().first().active == False

@pytest.mark.django_db
def test_connect_form_increments_retry_count(parent, child):
    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert models.ParentConnection.objects.all().first().retries == 0
    models.ParentConnection.objects.all().update(removed=True)
    form = forms.parent.ConnectForm(instance=parent.profile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert models.ParentConnection.objects.all().first().retries == 1

@pytest.mark.django_db
def test_parents_only_decorator(rf, parent):
    request = rf.get('/path')
    view = mock.Mock()
    request.user = AnonymousUser()
    with pytest.raises(PermissionDenied):
        response = decorators.parents_only(view)(request)
        assert not view.called
    request.user = parent
    response = decorators.parents_only(view)(request)
    assert view.called

@pytest.mark.django_db
def test_connected_parent_only_decorator(rf, parent, child):
    connection = models.ParentConnection.objects.create(child_profile=child.profile, parent_profile=parent.profile)
    request = rf.get('/path')
    view = mock.Mock()
    request.user = child
    with pytest.raises(PermissionDenied):
        response = decorators.connected_parent_only(view)(request, connection_id=connection.id)
        assert not view.called
    request.user = parent
    response = decorators.connected_parent_only(view)(request, connection_id=connection.id)
    assert view.called

@pytest.mark.django_db
def test_active_connected_parent_only_decorator(rf, parent, child):
    connection = models.ParentConnection.objects.create(child_profile=child.profile, parent_profile=parent.profile)
    request = rf.get('/path')
    view = mock.Mock()
    request.user = parent
    with pytest.raises(PermissionDenied):
        response = decorators.active_connected_parent_only(view)(request, connection_id=connection.id)
        assert not view.called
    connection.active = True
    connection.save()
    response = decorators.active_connected_parent_only(view)(request, connection_id=connection.id)
    assert view.called
