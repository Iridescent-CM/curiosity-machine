import mock
import pytest

from django.http import *
from students.factories import *
from surveys.factories import *
from ..factories import *
from ..awardforce import *

@pytest.mark.django_db
def test_integrating_redirects():
    submitter = mock.Mock()
    submitter.has_verified_email.return_value = True
    submitter.get_login_url.return_value = '/some/url'
    res = Integrating(submitter=submitter).run()
    assert isinstance(res, HttpResponseRedirect)
    assert res.url == '/some/url'

@pytest.mark.django_db
def test_integrating_forbids_unverified_email():
    user = FamilyFactory()
    assert isinstance(Integrating(user).run(), HttpResponseForbidden)

@pytest.mark.django_db
def test_submitter_has_verified_email():
    user = FamilyFactory()
    assert not AwardForceSubmitter(user).has_verified_email()
    email = EmailAddress.objects.get_primary(user)
    email.verified = True
    email.save()
    assert AwardForceSubmitter(user).has_verified_email()

@pytest.mark.django_db
def test_submitter_getting_url_sets_slug():
    api = mock.MagicMock()
    api.create_user.return_value = 'slug'
    api.get_auth_token.return_value = 'token'
    user = FamilyFactory()
    submitter = AwardForceSubmitter(user, api=api)
    assert not hasattr(user, 'awardforceintegration')
    submitter.get_login_url()
    assert user.awardforceintegration.slug == 'slug'

@pytest.mark.django_db
def test_checklist_checks_email_unique():
    user = FamilyFactory()
    FamilyFactory()
    assert AwardForceChecklist(user).email_unique

@pytest.mark.django_db
def test_checklist_checks_email_unique_against_family_only():
    user = FamilyFactory()
    StudentFactory(email=user.email)
    assert AwardForceChecklist(user).email_unique

@pytest.mark.django_db
def test_checklist_catches_non_unique_email():
    user = FamilyFactory()
    FamilyFactory(email=user.email)
    assert not AwardForceChecklist(user).email_unique

@pytest.mark.django_db
def test_checklist_catches_unverified_email():
    user = FamilyFactory()
    assert not AwardForceChecklist(user).email_verified
    user = FamilyFactory(sync_email=True)
    assert not AwardForceChecklist(user).email_verified

@pytest.mark.django_db
def test_checklist_checks_email_verified():
    user = FamilyFactory(sync_email=True)
    email = EmailAddress.objects.get_primary(user)
    email.verified = True
    email.save()
    assert AwardForceChecklist(user).email_verified

@pytest.mark.django_db
def test_checklist_checks_post_survey_result():
    user = FamilyFactory()
    SurveyResponseFactory(user=user, survey_id=AwardForceChecklist.post_survey.id, status='COMPLETED')
    assert AwardForceChecklist(user).post_survey_taken

@pytest.mark.django_db
def test_checklist_catches_post_survey_not_taken():
    user = FamilyFactory()
    assert not AwardForceChecklist(user).post_survey_taken

    user2 = FamilyFactory()
    SurveyResponseFactory(user=user2, survey_id=AwardForceChecklist.post_survey.id, status='UNKNOWN')
    assert not AwardForceChecklist(user2).post_survey_taken
