from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Progress, Example
from curiositymachine import signals

@receiver(post_save, sender=Progress)
def create_progress(sender, instance, created, **kwargs):
    if created and instance.is_first_project():
        signals.started_first_project.send(sender=instance.student, progress=instance)

@receiver(post_save, sender=Example)
def create_example(sender, instance, created, **kwargs):
    if created:
        progress = instance.progress
        signals.approved_project_for_gallery.send(sender=progress.mentor, example=instance)

