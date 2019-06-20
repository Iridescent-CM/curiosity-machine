import pytest
from django.contrib.auth import get_user_model
from memberships.factories import *
from surveys import get_survey
from surveys.models import ResponseStatus
from ..factories import *

def test_user_type():
    assert EducatorFactory.build().extra.user_type == 'educator'
