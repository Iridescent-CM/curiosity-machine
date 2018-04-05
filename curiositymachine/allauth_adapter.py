from allauth.account.adapter import DefaultAccountAdapter
from curiositymachine.context_processors.google_analytics import add_event
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from smtplib import SMTPException
import logging

logger = logging.getLogger(__name__)

ALLOWED_MESSAGES = [
    'account/messages/password_changed.txt',
]

class AllAuthAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        if message_template in ALLOWED_MESSAGES:
            super().add_message(request, level, message_template, message_context=None, extra_tags='')
        else:
            pass  # allauth stahp

    def send_mail(self, template_prefix, email, context):
        try:
            super().send_mail(template_prefix, email, context)
        except (ConnectionRefusedError, SMTPException) as e:
            if settings.DEBUG:
                # running with DEBUG and no SMTP is okay
                logger.exception("Exception encountered sending mail, DEBUG on")
            else:
                raise e

    def confirm_email(self, request, email_address):
        email_address.set_as_primary()
        return super().confirm_email(request, email_address)

    def authenticate(self, request, **credentials):
        try:
            return super().authenticate(request, **credentials)
        except MultipleObjectsReturned:
            logger.error("Duplicate usernames found on login for %s:" % credentials.get("username"), exc_info=True)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=commit)
        add_event(request, "account", "create")
        return user
