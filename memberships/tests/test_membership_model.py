import mock
import pytest
from challenges.factories import ChallengeFactory
from datetime import timedelta
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from django.utils.timezone import now, localtime
from educators.factories import *
from memberships.factories import MembershipFactory
from memberships.models import Membership
from mentors.factories import *
from profiles.factories import *
from profiles.models import UserRole
from students.factories import *

@pytest.fixture
def rightnow():
    return localtime(now())

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

@pytest.mark.django_db
def test_filter_by_challenge_access():
    challenge1 = ChallengeFactory()
    challenge2 = ChallengeFactory()
    user = StudentFactory()

    assert not Membership.filter_by_challenge_access(user, [challenge1.id, challenge2.id])

    membership = MembershipFactory(members=[user], challenges=[challenge1])

    assert set(Membership.filter_by_challenge_access(user, [challenge1.id, challenge2.id])) == set([challenge1.id])
    
@pytest.mark.django_db
def test_filter_by_challenge_access_for_free_challenge():
    challenge = ChallengeFactory(free=True)
    user = AnonymousUser()
    student = StudentFactory()

    assert set(Membership.filter_by_challenge_access(user, [challenge.id])) == set([challenge.id])
    assert set(Membership.filter_by_challenge_access(student, [challenge.id])) == set([challenge.id])

@pytest.mark.django_db
def test_filter_by_challenge_access_for_anonymous():
    challenge = ChallengeFactory()
    user = AnonymousUser()

    assert not Membership.filter_by_challenge_access(user, [challenge.id])

@pytest.mark.django_db
def test_filter_by_challenge_access_user_type_exemptions():
    challenge = ChallengeFactory()
    mentor = MentorFactory()
    staff = UserFactory(is_staff=True)

    assert set(Membership.filter_by_challenge_access(mentor, [challenge.id])) == set([challenge.id])
    assert set(Membership.filter_by_challenge_access(staff, [challenge.id])) == set([challenge.id])

@pytest.mark.django_db
def test_filter_by_challenge_access_for_inactive_membership():
    challenge1 = ChallengeFactory()
    challenge2 = ChallengeFactory()
    user = StudentFactory()
    membership = MembershipFactory(members=[user], challenges=[challenge1])

    assert set(Membership.filter_by_challenge_access(user, [challenge1.id, challenge2.id])) == set([challenge1.id])
    membership.is_active = False
    membership.save()
    assert not Membership.filter_by_challenge_access(user, [challenge1.id, challenge2.id])

@pytest.mark.django_db
def test_share_membership():
    users = UserFactory.create_batch(3)
    membership = MembershipFactory(members=users[0:2])

    assert Membership.share_membership(users[0].username, users[1].username)
    assert not Membership.share_membership(users[0].username, users[2].username)

@pytest.mark.django_db
def test_share_membership_for_inactive():
    users = UserFactory.create_batch(2)
    membership = MembershipFactory(members=users, is_active=False)

    assert not Membership.share_membership(users[0].username, users[1].username)

@pytest.mark.django_db
def test_expired_manager_method(rightnow):
    yesterday = MembershipFactory(expiration=rightnow - timedelta(days=1))
    today = MembershipFactory(expiration=rightnow)
    tomorrow = MembershipFactory(expiration=rightnow + timedelta(days=1))

    assert set(Membership.objects.expired()) == set([yesterday])
    assert set(Membership.objects.expired(expiration=rightnow + timedelta(days=1))) == set([yesterday, today])

@pytest.mark.django_db
def test_expired_with_cutoff_manager_method(rightnow):
    today = MembershipFactory(expiration=rightnow)
    yesterday = MembershipFactory(expiration=rightnow - timedelta(days=1))
    twodaysago = MembershipFactory(expiration=rightnow - timedelta(days=2))

    assert set(Membership.objects.expired()) == set([yesterday, twodaysago])
    assert set(Membership.objects.expired(cutoff=rightnow - timedelta(days=1))) == set([yesterday])

@pytest.mark.django_db
def test_expiring_manager_method(rightnow):
    yesterday = MembershipFactory(expiration=rightnow - timedelta(days=1))
    today = MembershipFactory(expiration=rightnow)
    tomorrow = MembershipFactory(expiration=rightnow + timedelta(days=1))
    twomonths = MembershipFactory(expiration=rightnow + timedelta(days=60))

    assert set(Membership.objects.expiring()) == set([today, tomorrow])
    assert set(Membership.objects.expiring(cutoff=rightnow)) == set([today])

def test_show_expiring_notice():
    inayear = localtime(now()).date() + timedelta(days=365)
    inaweek = localtime(now()).date() + timedelta(days=7)
    today = localtime(now()).date()
    yesterday = localtime(now()).date() - timedelta(days=1)

    assert not MembershipFactory.build().show_expiring_notice()
    assert not MembershipFactory.build(expiration=inayear).show_expiring_notice()
    assert MembershipFactory.build(expiration=inaweek).show_expiring_notice()
    assert MembershipFactory.build(expiration=today).show_expiring_notice()
    assert not MembershipFactory.build(expiration=yesterday).show_expiring_notice()
    assert not MembershipFactory.build(expiration=inaweek, is_active=False).show_expiring_notice()

    with mock.patch('memberships.models.settings') as settings:
        settings.MEMBERSHIP_EXPIRING_NOTICE_DAYS = 5
        assert not MembershipFactory.build(expiration=inaweek).show_expiring_notice()
        assert MembershipFactory.build(expiration=today).show_expiring_notice()

@pytest.mark.django_db
def test_user_type_members_helpers():
    students = StudentFactory.create_batch(5)
    educators = EducatorFactory.create_batch(4)

    membership = MembershipFactory(members=students+educators)

    assert set(membership.educators.all()) == set(educators)
    assert set(membership.students.all()) == set(students)
