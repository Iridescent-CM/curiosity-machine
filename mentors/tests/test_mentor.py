import pytest
from ..factories import *

def test_user_type():
    assert MentorFactory.build().extra.user_type == 'mentor'
