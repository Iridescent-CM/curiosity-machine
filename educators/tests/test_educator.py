import pytest
from ..factories import *

def test_user_type():
    assert EducatorFactory.build().extra.user_type == 'educator'
