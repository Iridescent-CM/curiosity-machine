import pytest
from mock import MagicMock

from django.utils.timezone import now
from datetime import timedelta

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
