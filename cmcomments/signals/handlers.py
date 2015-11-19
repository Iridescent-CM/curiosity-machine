from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Stage
from cmcomments.models import Comment

@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    if created:
        if instance.stage == Stage.reflect.value and instance.image:
            instance.email_student_completed()
