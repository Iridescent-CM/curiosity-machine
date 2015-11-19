from curiositymachine import signals
from django.dispatch import receiver

@receiver(signals.student.first_project_started)
def send(sender, progress, **kwargs):
    progress.email_first_project()