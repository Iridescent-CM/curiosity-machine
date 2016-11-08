import pytest
from mock import MagicMock

from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
User = get_user_model()

from profiles.factories import *

from ..sorting import *

def test_reversed():
    l = [1,2,3,4]
    assert sorted(l, reverse=True) == [i.value for i in sorted([Reversed(i) for i in l])]

def test_latest_student_comment_sort():
    mocks = [MagicMock() for i in range(5)]
    mocks[0].latest_student_comment = None
    mocks[0].challenge.name = 'B'
    mocks[1].latest_student_comment = None
    mocks[1].challenge.name = 'A'
    mocks[2].latest_student_comment.created = now() - timedelta(days=2)
    mocks[2].challenge.name = 'B'
    mocks[3].latest_student_comment.created = now() - timedelta(days=2)
    mocks[3].challenge.name = 'A'
    mocks[4].latest_student_comment.created = now() - timedelta(days=1)
    mocks[4].challenge.name = 'Z'

    assert sorted(mocks, key=latest_student_comment_sort) == list(reversed(mocks))

@pytest.mark.django_db
def test_student_sorter_by_first_name():
    users = [
        UserFactory(first_name='', username='b_user'),
        UserFactory(first_name='', username='a_user'),
        UserFactory(first_name='b_name'),
        UserFactory(first_name='a_name'),
    ]
    default_sorted_ids = list(StudentSorter()
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    named_sorted_ids = list(StudentSorter('first_name')
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert default_sorted_ids == [u.id for u in reversed(users)]
    assert named_sorted_ids == [u.id for u in reversed(users)]

@pytest.mark.django_db
def test_student_sorter_by_last_name():
    users = [
        UserFactory(last_name='', username='b_user'),
        UserFactory(last_name='', username='a_user'),
        UserFactory(last_name='b_name'),
        UserFactory(last_name='a_name'),
    ]
    sorted_ids = list(StudentSorter('last_name')
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert sorted_ids == [u.id for u in reversed(users)]

@pytest.mark.django_db
def test_student_sorter_by_username():
    users = [
        UserFactory(username='b_user'),
        UserFactory(username='a_user'),
    ]
    sorted_ids = list(StudentSorter('username')
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert sorted_ids == [u.id for u in reversed(users)]
