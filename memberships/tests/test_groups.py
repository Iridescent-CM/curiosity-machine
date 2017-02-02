import pytest

from ..factories import *
from profiles.factories import *

from ..models import Group, GroupMember
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_group_and_member_membership_validation():
    user = UserFactory()
    group = GroupFactory()
    member = MemberFactory(user=user)
    groupmember = GroupMember(group=group, member=member)
    with pytest.raises(ValidationError) as e:
        groupmember.save()

    assert "part of the same membership" in str(e.value)

@pytest.mark.django_db
def test_only_students_in_groups():
    user = UserFactory()
    group = GroupFactory()
    member = MemberFactory(user=user, membership=group.membership)
    groupmember = GroupMember(group=group, member=member)
    with pytest.raises(ValidationError) as e:
        groupmember.save()
    
    assert "Only students" in str(e.value)