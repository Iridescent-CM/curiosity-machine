from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AllAuthAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
            message_context=None, extra_tags=''):
        pass  # allauth stahp

    def send_mail(self, template_prefix, email, context):
        try:
            super().send_mail(template_prefix, email, context)
        except ConnectionRefusedError as e:
            if settings.DEBUG:
                # running with DEBUG and no SMTP is okay
                logger.exception("Exception encountered sending mail, DEBUG on")
            else:
                raise e