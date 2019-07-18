import pytest
from ..factories import *
from surveys.factories import *
from surveys.models import *
from django.conf import settings

def test_presurvey_required():
    assert FamilyProfileFactory.build(location__country='GB').presurvey_required
    assert FamilyProfileFactory.build(location__country='ES').presurvey_not_required

    assert not FamilyProfileFactory.build(location__country='GB').presurvey_not_required
    assert not FamilyProfileFactory.build(location__country='ES').presurvey_required

@pytest.mark.django_db
def test_full_access_granted_without_survey_when_not_required():
    account = FamilyFactory(familyprofile__location__country='ES')
    PermissionSlipFactory(account=account)
    assert account.familyprofile.check_full_access()

@pytest.mark.django_db
def test_full_access_granted_with_survey_when_required(settings):
    settings.SURVEY_FAMILY_PRE_LINK = 'x'
    settings.SURVEY_FAMILY_PRE_ACTIVE = 1

    account = FamilyFactory(familyprofile__location__country='GB')
    PermissionSlipFactory(account=account)
    assert not account.familyprofile.check_full_access()

    SurveyResponse.objects.filter(user=account).delete()
    SurveyResponseFactory(user=account, survey_id='FAMILY_PRE', status="COMPLETED")

    assert account.familyprofile.check_full_access()

@pytest.mark.django_db
def test_full_access_granted_with_permission_slip():
    account = FamilyFactory(familyprofile__location__country='ES')
    assert not account.familyprofile.check_full_access()

    PermissionSlipFactory(account=account)
    assert account.familyprofile.check_full_access()

