import pytest
from django.utils.timezone import now
from ..factories import *

def test_user_type():
    assert StudentFactory.build().extra.user_type == 'student'
    assert StudentFactory.build(studentprofile__birthday=now()).extra.user_type == 'underage student'
