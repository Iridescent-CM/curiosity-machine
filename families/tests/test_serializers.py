import mock
import pytest

from ..awardforce import *
from ..factories import *
from ..serializers import *

@pytest.mark.django_db
def test_that_it_serializes():
    assert ChecklistSerializer(AwardForceChecklist(FamilyFactory())).data