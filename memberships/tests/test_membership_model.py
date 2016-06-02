import pytest

from memberships.models import Membership

from profiles.models import UserRole

from django.db.utils import IntegrityError

@pytest.mark.django_db
def test_uniqueness():
    Membership(name="membership").save()
    with pytest.raises(IntegrityError):
        Membership(name="membership").save()

@pytest.mark.django_db
def test_limit_for():
    membership = Membership(name="membership")
    membership.save()
    assert membership.limit_for(UserRole.student.value) == None

    membership.memberlimit_set.create(limit=1, role=UserRole.student.value)
    assert membership.limit_for(UserRole.student.value) == 1
