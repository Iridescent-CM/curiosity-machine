import pytest

from memberships.models import Membership, Member, MemberLimit

from profiles.models import UserRole
from profiles.factories import StudentFactory, EducatorFactory

from django.core.exceptions import ValidationError
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
def test_member_limits_clean_enforces_limit():
    membership = Membership(name="membership")
    membership.save()
    MemberLimit(role=UserRole.student.value, limit=1, membership=membership).save()

    member = Member(membership=membership, user=StudentFactory())
    member.full_clean()
    member.save()
    with pytest.raises(ValidationError):
        member = Member(membership=membership, user=StudentFactory())
        member.full_clean()
        member.save()
    member = Member(membership=membership, user=EducatorFactory())
    member.full_clean()
    member.save()

    assert membership.members.count() == 2