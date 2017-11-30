from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from profiles.models import UserExtra, User, BaseProfile
from curiositymachine import signals

@receiver(post_save, sender=get_user_model())
@receiver(post_save, sender=User)
def create_user_extra(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        if not hasattr(instance, "extra"):
            UserExtra.objects.create(user=instance)
        signals.created_account.send(sender=instance)

@receiver(post_save)
def create_profile(sender, instance, created, **kwargs):
    if created and issubclass(sender, BaseProfile):
        if kwargs.get('raw'):
            return
        signals.created_profile.send(sender=instance.user)