import pytest

from memberships.models import Member, Membership, MemberLimit
from profiles.models import UserRole

from profiles.factories import StudentFactory, EducatorFactory

from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_member_clean_enforces_limit():
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

@pytest.mark.django_db
def test_model_cleaned_on_save():
    membership = Membership(name="membership")
    membership.save()
    MemberLimit(role=UserRole.student.value, limit=0, membership=membership).save()

    member = Member(membership=membership, user=StudentFactory())
    with pytest.raises(ValidationError):
        member.save()
