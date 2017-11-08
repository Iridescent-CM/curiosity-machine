from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from profiles.models import UserExtra
from curiositymachine import signals

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        if not hasattr(instance, "extra"):
            UserExtra.objects.create(user=instance)
        signals.created_account.send(sender=instance)

# TODO: move this it at this point
from students.models import StudentProfile

@receiver(post_save, sender=StudentProfile)
def auto_approve_non_coppa_students(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw'):
        if not instance.is_underage():
            instance.user.extra.approved = True
            instance.user.extra.save(update_fields=['approved'])