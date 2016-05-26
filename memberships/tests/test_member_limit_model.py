import pytest

from memberships.models import Membership, MemberLimit, Member

from profiles.models import UserRole
from profiles.factories import StudentFactory

from django.db.utils import IntegrityError

@pytest.mark.django_db
def test_member_limit_uniqueness():
    membership = Membership(name="membership")
    membership.save()
    MemberLimit(membership=membership, role=UserRole.educator.value, limit = 1).save()
    MemberLimit(membership=membership, role=UserRole.student.value, limit = 1).save()
    with pytest.raises(IntegrityError):
        limit = MemberLimit(membership=membership, role=UserRole.educator.value, limit = 5)
        limit.save()

@pytest.mark.django_db
def test_current_count():
    membership = Membership(name="membership")
    membership.save()
    limit = MemberLimit(membership=membership, role=UserRole.student.value, limit = 1)
    limit.save()
    
    assert limit.current == 0
    Member(membership=membership, user=StudentFactory()).save()
    assert limit.current == 1