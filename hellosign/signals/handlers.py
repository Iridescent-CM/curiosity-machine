from curiositymachine import signals
from django.dispatch import receiver
from ..models import StudentConsentTemplate


@receiver(signals.created_profile)
def send_consent_email(sender, **kwargs):
    if (sender.extra.send_welcome
        and sender.extra.is_student
        and not sender.studentprofile.full_access
    ):
        StudentConsentTemplate().signature(sender)
