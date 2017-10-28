import pytest
import mock
from django.http import Http404
from django.utils.timezone import now, localtime
from datetime import timedelta
from ...decorators import MembershipSelection

from ...factories import *
from memberships.factories import *

def test_membership_selection_no_memberships(rf):
    request = rf.get('/home')
    memberships = []
    ms = MembershipSelection(request, memberships)
    assert ms.all == []
    assert ms.selected == None
    assert ms.count == 0
    assert ms.names == "None"
    assert ms.no_memberships
    assert not ms.memberships

def test_membership_selection_one_membership(rf):
    request = rf.get('/home')
    memberships = [MembershipFactory.build(id=5, display_name="name")]
    request.session = mock.MagicMock()

    ms = MembershipSelection(request, memberships)
    assert ms.count == 1
    assert ms.all == memberships
    assert ms.selected == memberships[0]
    assert ms.names == "name"
    assert not ms.no_memberships
    assert ms.memberships

def test_membership_selection_many_memberships(rf):
    request = rf.get('/home')
    memberships = [
        MembershipFactory.build(id=5, display_name="name"),
        MembershipFactory.build(id=6, display_name="name"),
    ]
    request.session = mock.MagicMock()

    ms = MembershipSelection(request, memberships)
    assert ms.count == 2
    assert ms.all == memberships
    assert ms.selected == memberships[0]
    assert ms.names == "name, name"
    assert not ms.no_memberships
    assert ms.memberships


def test_membership_selection_through_default(rf):
    request = rf.get('/home')
    memberships = [
        MembershipFactory.build(id=5, display_name="name"),
        MembershipFactory.build(id=6, display_name="name"),
    ]
    request.session = mock.MagicMock()

    ms = MembershipSelection(request, memberships)
    assert ms.selected.id == 5

def test_membership_selection_through_query_param(rf):
    request = rf.get('/home', {'m': '6'})
    memberships = [
        MembershipFactory.build(id=5, display_name="name"),
        MembershipFactory.build(id=6, display_name="name"),
    ]
    request.session = {}

    ms = MembershipSelection(request, memberships)
    assert ms.selected.id == 6
    assert request.session == {"active_membership": 6}

def test_membership_selection_through_session_variable(rf):
    request = rf.get('/home')
    memberships = [
        MembershipFactory.build(id=5, display_name="name"),
        MembershipFactory.build(id=6, display_name="name"),
    ]
    request.session = {"active_membership": 6}

    ms = MembershipSelection(request, memberships)
    assert ms.selected.id == 6

def test_membership_selection_404s_on_non_int_query_param(rf):
    request = rf.get('/home', {'m': 'x'})
    memberships = [MembershipFactory.build(id=5, display_name="name")]
    request.session = mock.MagicMock()

    with pytest.raises(Http404):
        MembershipSelection(request, memberships)

def test_membership_selection_404s_on_bad_id_query_param(rf):
    request = rf.get('/home', {'m': '10'})
    memberships = [MembershipFactory.build(id=5, display_name="name")]
    request.session = mock.MagicMock()

    with pytest.raises(Http404):
        MembershipSelection(request, memberships)

def test_membership_selection_recovers_from_bad_id_in_session(rf):
    request = rf.get('/home')
    memberships = [MembershipFactory.build(id=5, display_name="name")]
    request.session = {"active_membership": 10}

    ms = MembershipSelection(request, memberships)
    assert "active_membership" not in request.session
    assert ms.selected == memberships[0]

@pytest.mark.django_db
def test_membership_selection_gets_user_memberships(rf):
    user = UserFactory()
    memberships = MembershipFactory.create_batch(3, members=[user])
    request = rf.get('/home')
    request.session = {}
    request.user = user

    ms = MembershipSelection(request)
    assert set([m.id for m in ms.all]) == set([m.id for m in memberships])

@pytest.mark.django_db
def test_membership_selection_skips_inactive_memberships(rf):
    user = UserFactory()
    memberships = MembershipFactory(is_active=False, members=[user])
    request = rf.get('/home')
    request.session = {}
    request.user = user

    ms = MembershipSelection(request)
    assert not ms.all

@pytest.mark.django_db
def test_membership_selection_recently_expired(rf):
    today = localtime(now()).date()
    yesterday = today - timedelta(days=1)
    lastweek = today - timedelta(days=7)
    twomonthsago = today - timedelta(days=61)
    user = UserFactory()
    memberships = [
        MembershipFactory(expiration=today, members=[user]),
        MembershipFactory(expiration=yesterday, members=[user]),
        MembershipFactory(expiration=lastweek, members=[user]),
        MembershipFactory(expiration=twomonthsago, members=[user]),
    ]
    request = rf.get('/home')
    request.session = {}
    request.user = user

    ms = MembershipSelection(request)
    assert set(ms.recently_expired) == set(memberships[1:3])
