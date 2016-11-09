import pytest
from mock import MagicMock

from django.utils.timezone import now
from datetime import timedelta
from django.http.request import QueryDict
from django.contrib.auth import get_user_model
User = get_user_model()

from profiles.factories import *

from ..sorting import *

def test_reversed():
    l = [1,2,3,4]
    assert sorted(l, reverse=True) == [i.value for i in sorted([Reversed(i) for i in l])]

def test_latest_user_comment_sort():
    mocks = [MagicMock() for i in range(5)]
    mocks[0].latest_user_comment = None
    mocks[0].challenge.name = 'B'
    mocks[1].latest_user_comment = None
    mocks[1].challenge.name = 'A'
    mocks[2].latest_user_comment.created = now() - timedelta(days=2)
    mocks[2].challenge.name = 'B'
    mocks[3].latest_user_comment.created = now() - timedelta(days=2)
    mocks[3].challenge.name = 'A'
    mocks[4].latest_user_comment.created = now() - timedelta(days=1)
    mocks[4].challenge.name = 'Z'

    assert sorted(mocks, key=latest_user_comment_sort) == list(reversed(mocks))

def test_student_sorter_strategy_short_names():
    assert StudentSorter.Strategy.first_name == StudentSorter.Strategy.f
    assert StudentSorter.Strategy.last_name == StudentSorter.Strategy.l
    assert StudentSorter.Strategy.username == StudentSorter.Strategy.u

@pytest.mark.django_db
def test_student_sorter_by_first_name():
    users = [
        UserFactory(first_name='', username='C_user'),
        UserFactory(first_name='', username='b_user'),
        UserFactory(first_name='', username='A_user'),
        UserFactory(first_name='c_name'),
        UserFactory(first_name='B_name'),
        UserFactory(first_name='a_name'),
    ]
    default_sorted_ids = list(StudentSorter()
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    named_sorted_ids = list(StudentSorter(StudentSorter.Strategy.first_name)
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert default_sorted_ids == [u.id for u in reversed(users)]
    assert named_sorted_ids == [u.id for u in reversed(users)]

@pytest.mark.django_db
def test_student_sorter_by_last_name():
    users = [
        UserFactory(last_name='', username='c_user'),
        UserFactory(last_name='', username='B_user'),
        UserFactory(last_name='', username='a_user'),
        UserFactory(last_name='C_name'),
        UserFactory(last_name='b_name'),
        UserFactory(last_name='A_name'),
    ]
    sorted_ids = list(StudentSorter(StudentSorter.Strategy.last_name)
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert sorted_ids == [u.id for u in reversed(users)]

@pytest.mark.django_db
def test_student_sorter_by_username():
    users = [
        UserFactory(username='c_user'),
        UserFactory(username='B_user'),
        UserFactory(username='a_user'),
    ]
    sorted_ids = list(StudentSorter(StudentSorter.Strategy.username)
        .sort(User.objects)
        .values_list('id', flat=True)
        .all())
    assert sorted_ids == [u.id for u in reversed(users)]

def test_strategy_type_error():
    with pytest.raises(TypeError):
        StudentSorter(strategy='nope')

def test_student_sorter_from_query():
    StudentSorter(query=QueryDict('')).strategy == StudentSorter.Strategy.first_name
    StudentSorter(query=QueryDict('sort=f')).strategy == StudentSorter.Strategy.first_name
    StudentSorter(query=QueryDict('sort=l')).strategy == StudentSorter.Strategy.last_name
    StudentSorter(query=QueryDict('sort=u')).strategy == StudentSorter.Strategy.username
    StudentSorter(query=QueryDict('sort=l&sort=f')).strategy == StudentSorter.Strategy.first_name
    StudentSorter(param="foo", query=QueryDict('foo=f')).strategy == StudentSorter.Strategy.first_name

def test_student_sorter_context_helpers():
    assert StudentSorter().strategies() == [
        {"name": "First name", "url": "?sort=f"},
        {"name": "Last name", "url": "?sort=l"},
        {"name": "Username", "url": "?sort=u"},
    ]
    assert StudentSorter(param="foo").strategies() == [
        {"name": "First name", "url": "?foo=f"},
        {"name": "Last name", "url": "?foo=l"},
        {"name": "Username", "url": "?foo=u"},
    ]
    assert StudentSorter().strategies(base_url="http://base.url") == [
        {"name": "First name", "url": "http://base.url?sort=f"},
        {"name": "Last name", "url": "http://base.url?sort=l"},
        {"name": "Username", "url": "http://base.url?sort=u"},
    ]
    assert StudentSorter().selected() == "First name"
    assert StudentSorter(StudentSorter.Strategy.last_name).selected() == "Last name"
    assert StudentSorter(StudentSorter.Strategy.username).selected() == "Username"
