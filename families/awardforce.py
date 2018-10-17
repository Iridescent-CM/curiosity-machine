from allauth.account.models import EmailAddress
from django.conf import settings
from django.http import *
import logging
import requests

logger = logging.getLogger(__name__)

class Api(object):

    def __init__(self, *args, **kwargs):
        res = requests.get(
            'https://api.awardsplatform.com/access-token/',
            headers={
                "Accept": "application/vnd.Award Force.v1.0+json",
                "Authorization": "Basic %s" % settings.AWARDFORCE_API_KEY,
            }
        )
        self.access_token = res.text

    def create_user(self, **kwargs):
        res = requests.post(
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
        res = requests.get(
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


class AwardForceSubmitter(object):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.email_address = kwargs.get('email_address', EmailAddress.objects.get_primary(self.user))
        self.profile = kwargs.get('profile', self.user.familyprofile)
        self.api = kwargs.get('api', Api())

    def has_verified_email(self):
        return self.email_address and self.email_address.verified

    def has_slug(self):
        return bool(self.get_slug())

    def create_slug(self):
        user = self.user
        slug = self.api.create_user(email=user.email, first_name=user.first_name, last_name=user.last_name)
        self.profile.awardforce_slug = slug
        self.profile.save(update_fields=["awardforce_slug"])

    def get_slug(self):
        return self.profile.awardforce_slug

    def get_auth_token(self):
        if not self.has_slug():
            self.create_slug()
        return self.api.get_auth_token(self.get_slug())

    def get_login_url(self):
        token = self.get_auth_token()
        return self.api.get_login_url(token)


class Integrating(object):

    def __init__(self, user, *args, **kwargs):
        self.submitter = kwargs.get('submitter', AwardForceSubmitter(user))

    def run(self):
        submitter = self.submitter

        if not submitter.has_verified_email():
            return HttpResponseForbidden()

        url = submitter.get_login_url()

        return HttpResponseRedirect(url)
