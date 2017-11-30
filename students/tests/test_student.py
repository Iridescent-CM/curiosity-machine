import pytest
from django.utils.timezone import now
from profiles.factories import *
from ..factories import *
from ..models import *

def test_user_type():
    assert StudentFactory.build().extra.user_type == 'student'
    assert StudentFactory.build(studentprofile__birthday=now()).extra.user_type == 'underage student'

@pytest.mark.django_db
def test_non_coppa_students_auto_approve():
    user = UserFactory(extra__approved=False)
    profile = StudentProfileFactory.build(user=user)
    profile.save()
    assert user.extra.approved

@pytest.mark.django_db
def test_underage_students_do_not_auto_approve():
    user = UserFactory(extra__approved=False)
    profile = StudentProfileFactory.build(user=user, underage=True)
    profile.save()
    assert not user.extra.approved
