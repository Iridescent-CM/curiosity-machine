import datetime
from hellosign_sdk import HSClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_student_consent_form(sender):
    api_key = settings.HELLOSIGN_API_KEY
    client = HSClient(api_key=api_key)
    # autofill template fields:
    template_id = settings.STUDENT_CONSENT_TEMPLATE_ID
    parent_email = sender.email
    child_birth_date = sender.studentprofile.birthday.strftime('%b %d, %Y')
    child_username = sender.username
    child_user_id = str(sender.studentprofile.user_id)
    subject = "Curiosity Machine Parental Consent Form"
    message = 'Your child has requested the user name ' + child_username + \
              ' on Curiosity Machine, where they will be able to ' \
              'explore design challenges, build projects with ' \
              'easy-to-find materials, and watch inspirational ' \
              'videos featuring real scientists and engineers ' \
              'talking about their work.\n\nTo activate your' \
              ' child’s account, complete the parental consent' \
              ' form in this email.\n\nWe\'ll let you know when' \
              ' your child’s account is activated so you can' \
              ' start inventing together!'
    signers = [
        {"name": child_username, "email_address": parent_email, "role_name": "Parent"}
    ]
    custom_fields = [
        {settings.STUDENT_CONSENT_TEMPLATE_EMAIL_ID: parent_email,
         settings.STUDENT_CONSENT_TEMPLATE_USERNAME_ID: child_username}
    ]
    metadata = {
        "template_id" : template_id,
        "user_id": child_user_id,
	"environment_name": settings.HELLOSIGN_ENVIRONMENT_NAME
    }
    test_mode=not settings.HELLOSIGN_PRODUCTION_MODE


    # send template:
    try:
        client.send_signature_request_with_template(test_mode=test_mode,
                                                    template_id=template_id,
                                                    custom_fields=custom_fields, signers=signers,
                                                    subject=subject,
                                                    message=message,
                                                    metadata=metadata)
    except:
        logger.warning(
            "Unsent hellosign signature request, user_id=%s",
            child_user_id)
        raise
