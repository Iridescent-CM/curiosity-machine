import datetime
from hellosign_sdk import HSClient
from django.conf import settings


def send_underage_consent_form(sender):
    # For underage users we will be using the Hellosign
    # esignature api. The following code handles that:
    # Initialize HSClient using api key
    api_key = settings.HELLOSIGN_API_KEY
    client = HSClient(api_key=api_key)
    # autofill template fields:
    template_id = settings.UNDERAGE_CONSENT_TEMPLATE_ID
    parent_email = sender.email
    child_birth_date = sender.studentprofile.birthday.strftime('%b %d, %Y')
    child_username = sender.username
    child_user_id = str(sender.studentprofile.user_id)
    subject = "Activate Your Curiosity Machine Account"
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
        {settings.UNDERAGE_CONSENT_TEMPLATE_EMAIL_ID: parent_email,
         settings.UNDERAGE_CONSENT_TEMPLATE_BIRTHDAY_ID: child_birth_date,
         settings.UNDERAGE_CONSENT_TEMPLATE_USERNAME_ID: child_username}
    ]
    metadata = {
        "template_id" : template_id,
        "user_id": child_user_id}


    # send template:
    client.send_signature_request_with_template(test_mode=True,
                                                template_id=template_id,
                                                custom_fields=custom_fields, signers=signers,
                                                subject=subject,
                                                message=message,
                                                metadata=metadata)