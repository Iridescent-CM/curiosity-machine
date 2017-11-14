import mock
import pytest
from curiositymachine.middleware import UserProxyMiddleware
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from students.factories import *
from .. import decorators
from ..factories import *
from ..forms import *
from ..models import *

User = get_user_model()

@pytest.fixture
def parent():
    return ParentFactory()

@pytest.fixture
def child():
    return StudentFactory(username="child")

def test_user_type():
    assert ParentFactory.build().extra.user_type == 'parent'

def test_connect_form_requires_usernames():
    form = ConnectForm(data={})
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'required'

@pytest.mark.django_db
def test_connect_form_validates_existance():
    form = ConnectForm(data={
        "usernames": "nope"
    })
    assert not form.is_valid()
    assert "usernames" in form.errors.as_data()
    assert form.errors.as_data()["usernames"][0].code == 'nonexistant-user'

@pytest.mark.django_db
def test_connect_form_connects_to_usernames(parent, child):
    form = ConnectForm(instance=parent.parentprofile, data={
        "usernames": "child"
    })
    assert form.is_valid()
    assert ParentConnection.objects.all().count() == 0
    form.save()
    assert ParentConnection.objects.all().count() == 1
    assert [profile.id for profile in parent.parentprofile.child_profiles.all()] == [child.studentprofile.id]

@pytest.mark.django_db
def test_connect_form_reuses_and_resets_parentconnection_objects(parent, child):
    form = ConnectForm(instance=parent.parentprofile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    conn = ParentConnection.objects.all().first()
    conn.active = True
    conn.removed = True
    conn.save()
    form = ConnectForm(instance=parent.parentprofile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert ParentConnection.objects.all().count() == 1
    assert ParentConnection.objects.all().first().removed == False
    assert ParentConnection.objects.all().first().active == False

@pytest.mark.django_db
def test_connect_form_increments_retry_count(parent, child):
    form = ConnectForm(instance=parent.parentprofile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert ParentConnection.objects.all().first().retries == 0
    ParentConnection.objects.all().update(removed=True)
    form = ConnectForm(instance=parent.parentprofile, data={
        "usernames": "child"
    })
    form.is_valid()
    form.save()
    assert ParentConnection.objects.all().first().retries == 1

@pytest.mark.django_db
def test_connected_parent_only_decorator(rf, parent, child):
    connection = ParentConnection.objects.create(
        child_profile=child.studentprofile, parent_profile=parent.parentprofile
    )
    request = rf.get('/path')
    view = mock.Mock()

    request.user = child
    UserProxyMiddleware().process_request(request)
    with pytest.raises(PermissionDenied):
        response = decorators.connected_parent_only(view)(request, connection_id=connection.id)
        assert not view.called

    request.user = parent
    UserProxyMiddleware().process_request(request)
    response = decorators.connected_parent_only(view)(request, connection_id=connection.id)
    assert view.called

@pytest.mark.django_db
def test_active_connected_parent_only_decorator(rf, parent, child):
    connection = ParentConnection.objects.create(
        child_profile=child.studentprofile, parent_profile=parent.parentprofile
    )
    request = rf.get('/path')
    view = mock.Mock()

    request.user = parent
    UserProxyMiddleware().process_request(request)
    with pytest.raises(PermissionDenied):
        response = decorators.active_connected_parent_only(view)(request, connection_id=connection.id)
        assert not view.called
    connection.active = True
    connection.save()
    response = decorators.active_connected_parent_only(view)(request, connection_id=connection.id)
    assert view.called

@pytest.mark.django_db
def test_connected_child_only_decorator(rf, parent, child):
    connection = ParentConnection.objects.create(child_profile=child.studentprofile, parent_profile=parent.parentprofile)
    request = rf.get('/path')
    view = mock.Mock()
    request.user = parent
    UserProxyMiddleware().process_request(request)
    with pytest.raises(PermissionDenied):
        response = decorators.connected_child_only(view)(request, connection_id=connection.id)
        assert not view.called
    request.user = child
    UserProxyMiddleware().process_request(request)
    response = decorators.connected_child_only(view)(request, connection_id=connection.id)
    assert view.called
