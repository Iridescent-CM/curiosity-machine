from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Progress, Example
from curiositymachine import signals

@receiver(post_save, sender=Example)
def create_example(sender, instance, created, **kwargs):
    if created:
        progress = instance.progress
        signals.inspiration_gallery_submission_created.send(sender=progress.student, example=instance)

