import mock
import pytest

from ..awardforce import *
from ..factories import *
from ..serializers import *

@pytest.mark.django_db
def test_that_it_serializes(settings):
    settings.SURVEY_FAMILY_PRE_SUBMISSION_LINK = 'x'
    assert ChecklistSerializer(AwardForceChecklist(FamilyFactory())).data