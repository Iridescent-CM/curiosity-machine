from hellosign import send_student_consent_form
from curiositymachine import signals
from django.dispatch import receiver


@receiver(signals.created_profile)
def send_consent_email(sender, **kwargs):
    if (sender.extra.send_welcome
        and sender.extra.is_student
        and not sender.studentprofile.full_access
    ):
        send_student_consent_form(sender)
