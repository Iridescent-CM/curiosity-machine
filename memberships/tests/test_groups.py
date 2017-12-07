import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from profiles.factories import *
from ..factories import *
from ..models import Group, GroupMember

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

@pytest.mark.django_db
def test_group_name_uniqueness():
    membership1 = MembershipFactory()
    membership2 = MembershipFactory()
    assert Group.objects.create(membership=membership1, name="name")
    assert Group.objects.create(membership=membership2, name="name")
    with pytest.raises(IntegrityError) as e:
        Group.objects.create(membership=membership1, name="name")