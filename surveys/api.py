from django.conf import settings
from urllib.parse import urljoin
import base64
import hashlib
import hmac
import requests

def generate_signature(payload, api_key, api_secret):

    """
    From Surveymonkey docs: https://developer.surveymonkey.com/api/v3/?python#webhook-callbacks
    :type payload: str The response body from the webhook exactly as you received it
    :type api_key: str Your API Key for you app (if you have one) otherwise your Client ID
    :type api_secret: str Your API Secret for your app
    :return: str
    """

    # ensure all strings passed in are ascii strings,
    # as hmac does not work on unicode

    key = ('%s&%s' % (api_key, api_secret)).encode("ascii")

    signature = hmac.new(
        key=key,
        msg=payload,
        digestmod=hashlib.sha1
    )

    signature_digest = signature.digest()

    return base64.b64encode(signature_digest)

class Surveymonkey():
    """
    Low-level API class that handles some config loading, webhook validation,
    and wraps requests library with session authentication for convenience.
    """

    def __init__(self, *args, **kwargs):
        self.access_token = kwargs.get("access_token", settings.SURVEYMONKEY_ACCESS_TOKEN)
        self.api_key = kwargs.get("api_key", settings.SURVEYMONKEY_API_KEY)
        self.api_secret = kwargs.get("api_secret", settings.SURVEYMONKEY_API_SECRET)
        self.base_url = kwargs.get("base_url", settings.SURVEYMONKEY_API_BASE_URL)

        self.session = requests.session()
        self.session.headers.update({
          "Authorization": "Bearer %s" % self.access_token,
          "Content-Type": "application/json"
        })

    def url(self, path):
        return urljoin(self.base_url, path)

    def post(self, path='/', payload={}):
        return self.session.post(self.url(path), json=payload)

    def patch(self, path='/', payload={}):
        return self.session.patch(self.url(path), json=payload)

    def get(self, path='/', payload={}):
        return self.session.get(self.url(path), params=payload)

    def valid(self, body, signature):
        return hmac.compare_digest(
            generate_signature(body, self.api_key, self.api_secret),
            signature
        )
