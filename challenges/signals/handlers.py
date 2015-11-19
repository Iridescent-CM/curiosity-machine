from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Progress, Example
from curiositymachine import signals

@receiver(post_save, sender=Progress)
def create_progress(sender, instance, created, **kwargs):
    if created and instance.is_first_project():
        signals.student.first_project_started.send(sender=instance.student, progress=instance)

@receiver(post_save, sender=Example)
def create_example(sender, instance, created, **kwargs):
    if created:
        progress = instance.progress
        progress.student.profile.deliver_publish_email(progress)

