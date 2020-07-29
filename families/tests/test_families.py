import pytest
from ..factories import *
from ..models import FamilyRole
from surveys.factories import *
from surveys.models import *
from django.conf import settings

def test_surveys_required():
    assert FamilyProfileFactory.build(location__country='GB').surveys_required
    assert not FamilyProfileFactory.build(location__country='ES').surveys_required

def test_presurvey_not_required():
    assert FamilyProfileFactory.build(location__country='ES').presurvey_not_required
    assert not FamilyProfileFactory.build(location__country='GB').presurvey_not_required

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

@pytest.mark.django_db
def test_family_size():
    account = FamilyFactory()
    assert account.familyprofile.family_size() == 0
    FamilyMemberFactory(account=account, family_role=FamilyRole.parent_or_guardian.value)
    assert account.familyprofile.family_size() == 1
    FamilyMemberFactory(account=account, family_role=FamilyRole.child.value)
    assert account.familyprofile.family_size() == 2

@pytest.mark.django_db
def test_parent_guardian_first_names():
    account = FamilyFactory()
    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.parent_or_guardian.value,
        first_name="fname",
        last_name="lname"
    )
    assert account.familyprofile.parent_guardian_first_names() == "fname"

    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.parent_or_guardian.value,
        first_name="fnametwo",
        last_name="lname"
    )
    assert account.familyprofile.parent_guardian_first_names() == "fname, fnametwo"

    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.child.value,
        first_name="childfname",
        last_name="lname"
    )
    assert account.familyprofile.parent_guardian_first_names() == "fname, fnametwo"

@pytest.mark.django_db
def test_children_first_names():
    account = FamilyFactory()
    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.child.value,
        first_name="fname",
        last_name="lname"
    )
    assert account.familyprofile.children_first_names() == "fname"

    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.child.value,
        first_name="fnametwo",
        last_name="lname"
    )
    assert account.familyprofile.children_first_names() == "fname, fnametwo"

    FamilyMemberFactory(
        account=account,
        family_role=FamilyRole.parent_or_guardian.value,
        first_name="pogname",
        last_name="lname"
    )
    assert account.familyprofile.children_first_names() == "fname, fnametwo"
