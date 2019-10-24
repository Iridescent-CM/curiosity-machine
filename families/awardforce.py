from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import *
from django.utils.functional import cached_property
from profiles.models import UserExtra
from surveys import get_survey
from .models import *
import logging
import requests

logger = logging.getLogger(__name__)

class ApiException(Exception):
    pass

class Api(object):

    @cached_property
    def access_token(self):
        res = self.request(
            'GET',
            'https://api.awardsplatform.com/access-token/',
            headers={
                "Accept": "application/vnd.Award Force.v1.0+json",
                "Authorization": "Basic %s" % settings.AWARDFORCE_API_KEY,
            }
        )
        return res.text

    def request(self, *args, **kwargs):
        try:
            res = requests.request(*args, **kwargs)
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as e:
            logger.exception("Error from AwardForce API")
            raise ApiException("Error communicating with AwardForce")


    def create_user(self, **kwargs):
        res = self.request(
            'POST',
            'https://api.awardsplatform.com/user/',
            headers={
                "Accept": "application/vnd.Award Force.v1.0+json",
                "Authorization": "Basic %s" % self.access_token,
                "X-Account-Id": settings.AWARDFORCE_ACCOUNT_ID,
            },
            data={
                "email":kwargs.get('email'),
                "firstName":kwargs.get('first_name'),
                "lastName":kwargs.get('last_name'),
            }
        )
        return res.json().get('slug')

    def get_auth_token(self, slug):
        res = self.request(
            'GET',
            'https://api.awardsplatform.com/user/%s/auth-token' % slug,
            headers={
                "Accept": "application/vnd.Award Force.v1.0+json",
                "Authorization": "Basic %s" % self.access_token,
                "X-Account-Id": settings.AWARDFORCE_ACCOUNT_ID,
            },
        )
        return res.json().get('auth_token')

    def get_login_url(self, token):
        return "https://my.curiositymachine.org/login?token=%s" % token

def get_primary_email_for(user):
    """
    Family users will have User.email, but not necessarily the corresponding EmailAddress object. This
    sets up that object if necessary.
    """
    primary = EmailAddress.objects.get_primary(user)
    if not primary:
        primary, created = EmailAddress.objects.get_or_create(user=user, email__iexact=user.email, defaults={"email": user.email, "primary": True})
    return primary

class AwardForceSubmitter(object):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.email_address = kwargs.get('email_address') or get_primary_email_for(user)
        self.profile = kwargs.get('profile', self.user.familyprofile)
        self.api = kwargs.get('api', Api())

    def has_verified_email(self):
        return self.email_address and self.email_address.verified

    def has_slug(self):
        return bool(self.get_slug())

    def create_slug(self):
        user = self.user
        slug = self.api.create_user(email=user.email, first_name=user.first_name, last_name=user.last_name)
        AwardForceIntegration.objects.create(user=user, email=user.email, slug=slug)

    def get_slug(self):
        try:
            return self.user.awardforceintegration.slug
        except AwardForceIntegration.DoesNotExist:
            return None

    def slug_valid(self):
        return self.user.awardforceintegration.email == self.user.email

    def update_slug(self):
        self.user.awardforceintegration.delete()
        self.create_slug()

    def get_auth_token(self):
        if not self.has_slug():
            self.create_slug()
        elif not self.slug_valid():
            self.update_slug()
        return self.api.get_auth_token(self.get_slug())

    def get_login_url(self):
        token = self.get_auth_token()
        self.user.awardforceintegration.save() # update auto timestamp
        return self.api.get_login_url(token)


class Integrating(object):

    def __init__(self, user=None, *args, **kwargs):
        self.submitter = kwargs.get('submitter') or AwardForceSubmitter(user)

    def run(self):
        submitter = self.submitter

        if not submitter.has_verified_email():
            return HttpResponseForbidden()

        url = submitter.get_login_url()

        return HttpResponseRedirect(url)

class AwardForceChecklist(object):

    post_survey = get_survey('FAMILY_PRE_SUBMISSION')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.email_address = kwargs.get('email_address') or get_primary_email_for(user)

    @property
    def email_unique(self):
        return UserExtra.objects.role('family').filter(user__email=self.user.email).count() == 1

    @property
    def email_has_not_been_used(self):
        return not AwardForceIntegration.objects.filter(email=self.user.email).exclude(user=self.user).exists()

    @property
    def email_verified(self):
        email = self.email_address
        return bool(email and email.verified)

    def resend_verification_email(self, request=None):
        return self.email_address.send_confirmation(request)

    @property
    def post_survey_response(self):
        return self.post_survey.response(self.user)

    @property
    def post_survey_taken(self):
        return self.post_survey_response.completed

    @property
    def family_confirmed_all_listed(self):
        return self.user.familyprofile.members_confirmed

    def confirm_family_members(self):
        profile = self.user.familyprofile
        profile.members_confirmed = True
        profile.save(update_fields=['members_confirmed'])

    @property
    def complete(self):
        return (
            self.email_verified and
            self.post_survey_taken and
            self.family_confirmed_all_listed and
            self.email_has_not_been_used
        )
