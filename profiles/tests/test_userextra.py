from datetime import timedelta
from django.utils.timezone import now
from educators.factories import *
from families.factories import *
from mentors.factories import *
from parents.factories import *
from students.factories import *
from ..models import UserExtra, UserRole
import pytest

@pytest.mark.parametrize("role", list(UserRole))
@pytest.mark.django_db
def test_role_queryset_method(role):
    users = [
        StudentFactory(),
        MentorFactory(),
        ParentFactory(),
        EducatorFactory(),
        FamilyFactory(),
    ]

    expected = set([u.extra for u in users if UserRole(u.extra.role) == role])
    assert set(UserExtra.objects.role(role.value).all()) == expected
    assert set(UserExtra.objects.role(role.name).all()) == expected
    assert set(UserExtra.objects.role(role.name.upper()).all()) == expected
    assert set(UserExtra.objects.role(role).all()) == expected

@pytest.mark.parametrize("role", list(UserRole))
@pytest.mark.django_db
def test_role_querysets(role):
    users = [
        StudentFactory(),
        MentorFactory(),
        ParentFactory(),
        EducatorFactory(),
        FamilyFactory(),
    ]

    if role.app_name:
        expected = set([u.extra for u in users if UserRole(u.extra.role) == role])
        assert set(getattr(UserExtra, role.app_name).all()) == expected

@pytest.mark.django_db
def test_inactive_since():
    last_active = now() - timedelta(days=10)
    user = StudentFactory(extra__last_active_on=last_active)
    assert UserExtra.objects.inactive_since(9).count() == 1
    assert UserExtra.objects.inactive_since(11).count() == 0
