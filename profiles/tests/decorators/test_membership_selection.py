import pytest
import mock
from django.http import Http404
from ...decorators import membership_selection

def test_membership_selection_no_memberships(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = []
    request.session = mock.MagicMock()

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result
    assert result["count"] == 0
    assert result["all"] == []
    assert result["selected"] == None
    assert result["names"] == "None"
    assert result["no_memberships"] 
    assert not result["memberships"]

def test_membership_selection_one_membership(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}]
    request.session = mock.MagicMock()

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result
    assert result["count"] == 1
    assert result["all"] == [{"id": 5, "display_name": "name"}]
    assert result["selected"] == {"id": 5, "display_name": "name"}
    assert result["names"] == "name"
    assert not result["no_memberships"] 
    assert result["memberships"]

def test_membership_selection_many_memberships(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}, {"id": 6, "display_name": "name"}]
    request.session = mock.MagicMock()

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result
    assert result["count"] == 2
    assert result["all"] == [{"id": 5, "display_name": "name"}, {"id": 6, "display_name": "name"}]
    assert result["selected"] == {"id": 5, "display_name": "name"}
    assert result["names"] == "name, name"
    assert not result["no_memberships"] 
    assert result["memberships"]


def test_membership_selection_through_default(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}, {"id": 6, "display_name": "name"}]
    request.session = mock.MagicMock()

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result 
    assert result["selected"]["id"] == 5

def test_membership_selection_through_query_param(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home', {'m': '6'})
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}, {"id": 6, "display_name": "name"}]
    request.session = {}

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result 
    assert result["selected"]["id"] == 6
    assert request.session == {"active_membership": 6}

def test_membership_selection_through_session_variable(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}, {"id": 6, "display_name": "name"}]
    request.session = {"active_membership": 6}

    wrapped(request)
    result = view.call_args[1]['membership_selection']
    assert result
    assert result["selected"]["id"] == 6

def test_membership_selection_404s_on_non_int_query_param(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home', {'m': 'x'})
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}]
    request.session = mock.MagicMock()

    with pytest.raises(Http404):
        wrapped(request)

def test_membership_selection_404s_on_bad_id_query_param(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home', {'m': '10'})
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}]
    request.session = mock.MagicMock()

    with pytest.raises(Http404):
        wrapped(request)

def test_membership_selection_recovers_from_bad_id_in_session(rf):
    view = mock.MagicMock()
    wrapped = membership_selection(view)
    request = rf.get('/home')
    request.user = mock.MagicMock()
    request.user.membership_set.order_by().values.return_value = [{"id": 5, "display_name": "name"}]
    request.session = {"active_membership": 10}

    wrapped(request)
    assert "active_membership" not in request.session
    result = view.call_args[1]['membership_selection']
    assert result["selected"] == {"id": 5, "display_name": "name"}
