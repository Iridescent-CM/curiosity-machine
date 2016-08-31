import pytest
from mock import MagicMock

from ..decorators import *

from profiles.factories import *
from memberships.factories import *

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser


@pytest.mark.django_db
def test_members_only_allows_members(rf):
    user = UserFactory()
    membership = MembershipFactory(members=[user])

    inner = MagicMock()
    view = members_only(inner)

    request = rf.get('/some/path')
    request.user = user
    response = view(request, membership_id=membership.id)

    assert inner.called
    
@pytest.mark.django_db
def test_members_only_denies_others(rf):
    membership = MembershipFactory(members=[])

    inner = MagicMock()
    view = members_only(inner)

    request = rf.get('/some/path')

    request.user = AnonymousUser()
    with pytest.raises(PermissionDenied):
        view(request, membership_id=membership.id)

    request.user = UserFactory()
    with pytest.raises(PermissionDenied):
        view(request, membership_id=membership.id)