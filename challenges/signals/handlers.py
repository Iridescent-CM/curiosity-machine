from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Progress, Example

@receiver(post_save, sender=Progress)
def create_progress(sender, instance, created, **kwargs):
    if created and instance.is_first_project():
        instance.email_first_project()

@receiver(post_save, sender=Example)
def create_example(sender, instance, created, **kwargs):
    if created:
        progress = instance.progress
        progress.student.profile.deliver_publish_email(progress)

