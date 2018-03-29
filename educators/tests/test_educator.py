import pytest
from django.contrib.auth import get_user_model
from memberships.factories import *
from surveys import get_survey
from surveys.models import ResponseStatus
from ..factories import *

def test_user_type():
    assert EducatorFactory.build().extra.user_type == 'educator'

@pytest.mark.django_db
def test_is_coach(settings):
    coaches = MembershipFactory()
    settings.AICHALLENGE_COACH_MEMBERSHIP_ID = coaches.id

    notcoach = EducatorFactory()
    assert not notcoach.educatorprofile.is_coach
    coach = EducatorFactory()
    MemberFactory(membership=coaches, user=coach)
    assert coach.educatorprofile.is_coach

@pytest.mark.django_db
def test_full_coach_access_with_active_survey(settings):
    coaches = MembershipFactory()
    settings.AICHALLENGE_COACH_MEMBERSHIP_ID = coaches.id
    settings.AICHALLENGE_COACH_PRE_SURVEY_ID = '987'
    settings.SURVEY_987_ACTIVE = 1

    notcoach = EducatorFactory()
    assert not notcoach.educatorprofile.full_coach_access

    coach = EducatorFactory()
    MemberFactory(membership=coaches, user=coach)
    assert not coach.educatorprofile.full_coach_access

    survey = get_survey('987').response(coach)
    survey.status = ResponseStatus.COMPLETED
    survey.save()

    coach = get_user_model().objects.get(id=coach.id)
    assert coach.educatorprofile.full_coach_access

@pytest.mark.django_db
def test_full_coach_access_with_inactive_survey(settings):
    coaches = MembershipFactory()
    settings.AICHALLENGE_COACH_MEMBERSHIP_ID = coaches.id
    settings.AICHALLENGE_COACH_PRE_SURVEY_ID = '987'
    settings.SURVEY_987_ACTIVE = ''

    notcoach = EducatorFactory()
    assert not notcoach.educatorprofile.full_coach_access

    coach = EducatorFactory()
    MemberFactory(membership=coaches, user=coach)
    assert coach.educatorprofile.full_coach_access
