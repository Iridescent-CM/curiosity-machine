import mock
import pytest

from django.http import *
from ..factories import *
from ..awardforce import *

@pytest.mark.django_db
def test_integrating_redirects():
    user = FamilyFactory()
    email = EmailAddress.objects.get_primary(user)
    email.verified = True
    email.save()
    assert isinstance(Integrating(user).run(), HttpResponseRedirect)

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
    assert not user.familyprofile.awardforce_slug
    submitter.get_login_url()
    assert user.familyprofile.awardforce_slug
