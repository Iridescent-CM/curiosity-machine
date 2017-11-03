from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from profiles.models import Profile, UserExtra
from curiositymachine import signals

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        if not hasattr(instance, "extra") and not kwargs.get('raw'):
            #Profile.objects.create(user=instance)
            UserExtra.objects.create(user=instance)
        signals.created_account.send(sender=instance)

@receiver(post_save, sender=Profile)
def auto_approve_non_coppa_students(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw'):
        if instance.is_student and not instance.is_underage():
            instance.approved = True
            instance.save(update_fields=['approved'])