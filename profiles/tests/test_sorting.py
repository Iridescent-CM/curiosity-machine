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

def test_progress_sorter_by_most_recent_comment():
    progresses = [MagicMock() for i in range(5)]
    progresses[0].latest_user_comment = None
    progresses[0].challenge.name = 'B'
    progresses[1].latest_user_comment = None
    progresses[1].challenge.name = 'A'
    progresses[2].latest_user_comment.created = now() - timedelta(days=2)
    progresses[2].challenge.name = 'B'
    progresses[3].latest_user_comment.created = now() - timedelta(days=2)
    progresses[3].challenge.name = 'A'
    progresses[4].latest_user_comment.created = now() - timedelta(days=1)
    progresses[4].challenge.name = 'Z'

    sorted_progresses = ProgressSorter(ProgressSorter.Strategy.most_recent_comment).sort(progresses)
    assert sorted_progresses == list(reversed(progresses))

def test_progress_sorter_by_challenge_name():
    progresses = [MagicMock() for i in range(3)]
    progresses[0].challenge.name = 'C'
    progresses[1].challenge.name = 'b'
    progresses[2].challenge.name = 'A'

    sorted_progresses = ProgressSorter(ProgressSorter.Strategy.challenge_name).sort(progresses)
    assert sorted_progresses == list(reversed(progresses))

class DemoSorter(Sorter):
    class Strategy(Sorter.Strategy):
        thing_a = 0
        a = 0
        thing_b = 1
        b = 1

    default = Strategy.thing_a
    shortnames = ['a', 'b']

def test_strategy_type_error():
    with pytest.raises(TypeError):
        Sorter(strategy='nope')

def test_sorter_from_query():
    DemoSorter(query=QueryDict('')).strategy == DemoSorter.Strategy.thing_a
    DemoSorter(query=QueryDict('sort=a')).strategy == DemoSorter.Strategy.thing_a
    DemoSorter(query=QueryDict('sort=b')).strategy == DemoSorter.Strategy.thing_b
    DemoSorter(query=QueryDict('sort=a&sort=b')).strategy == DemoSorter.Strategy.thing_b
    DemoSorter(param="foo", query=QueryDict('foo=a')).strategy == DemoSorter.Strategy.thing_a

def test_sorter_context_helpers():
    assert DemoSorter().strategies() == [
        {"name": "Thing a", "url": "?sort=a"},
        {"name": "Thing b", "url": "?sort=b"},
    ]
    assert DemoSorter(param="foo").strategies() == [
        {"name": "Thing a", "url": "?foo=a"},
        {"name": "Thing b", "url": "?foo=b"},
    ]
    assert DemoSorter().strategies(base_url="http://base.url") == [
        {"name": "Thing a", "url": "http://base.url?sort=a"},
        {"name": "Thing b", "url": "http://base.url?sort=b"},
    ]
    assert DemoSorter().selected() == "Thing a"
    assert DemoSorter(DemoSorter.Strategy.thing_b).selected() == "Thing b"
