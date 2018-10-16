from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

class AwardForce(object):

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
