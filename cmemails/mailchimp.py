import requests
import hashlib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def subscribe(user):
    if not settings.MAILCHIMP_API_KEY and settings.MAILCHIMP_LIST_ID:
        return

    dc = settings.MAILCHIMP_DATA_CENTER
    list_id = settings.MAILCHIMP_LIST_ID
    api_key = settings.MAILCHIMP_API_KEY
    user_hash = hashlib.md5(user.email.lower().encode("latin-1")).hexdigest()

    r = requests.put(
        'https://%s.api.mailchimp.com/3.0/lists/%s/members/%s' % (dc, list_id, user_hash),
        auth=requests.auth.HTTPBasicAuth('anystring', api_key),
        json={
            "email_address": user.email,
            "status_if_new": "subscribed",
            "merge_fields": {
                "First Name": user.first_name,
                "Last Name": user.last_name,
                "Username": user.username
            }
        }
    )
    if r.status_code != 200:
        logger.warning("Mailchimp list signup returned an error: %s", r.json())    
    
