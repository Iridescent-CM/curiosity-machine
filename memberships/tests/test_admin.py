import pytest

from ..admin import ExpirationFilter
from ..models import Membership
from django.utils.timezone import now
from datetime import timedelta

from ..factories import *

@pytest.mark.django_db
def test_expiration_filter_filters_correctly():
    memberships = [
        MembershipFactory(expiration=now() - timedelta(days=1)),
        MembershipFactory(expiration=now() + timedelta(days=1)),
        MembershipFactory(expiration=now() + timedelta(days=10)),
        MembershipFactory(expiration=None),
    ]
    request = None
    assert set(ExpirationFilter(request, {'expiry': 'expired'}, None, None).queryset(request, Membership.objects).all()) == set(memberships[0:1])
    assert set(ExpirationFilter(request, {'expiry': 'unexpired'}, None, None).queryset(request, Membership.objects).all()) == set(memberships[1:])
    assert set(ExpirationFilter(request, {'expiry': 'week'}, None, None).queryset(request, Membership.objects).all()) == set(memberships[1:2])
    assert set(ExpirationFilter(request, {'expiry': 'month'}, None, None).queryset(request, Membership.objects).all()) == set(memberships[1:3])
    assert set(ExpirationFilter(request, {'expiry': 'none'}, None, None).queryset(request, Membership.objects).all()) == set(memberships[3:])
