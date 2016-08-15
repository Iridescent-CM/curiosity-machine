import pytest

from profiles.factories import UserFactory, StudentFactory, MentorFactory
from challenges.factories import ChallengeFactory
from memberships.factories import MembershipFactory

from memberships.models import Membership
from profiles.models import UserRole

from django.db.utils import IntegrityError
from django.contrib.auth.models import AnonymousUser

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
def test_share_membership():
    users = UserFactory.create_batch(3)
    membership = MembershipFactory(members=users[0:2])

    assert Membership.share_membership(users[0].username, users[1].username)
    assert not Membership.share_membership(users[0].username, users[2].username)
