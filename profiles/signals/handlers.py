from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles.models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "profile") and not kwargs.get('raw'):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def auto_approve_non_coppa_students(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw'):
        if instance.is_student and not instance.is_underage():
            instance.approved = True
            instance.save(update_fields=['approved'])