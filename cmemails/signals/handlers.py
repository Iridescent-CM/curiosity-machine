from curiositymachine import signals
from django.dispatch import receiver
from cmemails import deliver_email

@receiver(signals.student.first_project_started)
def send(sender, progress, **kwargs):
    deliver_email('first_project', sender.profile)