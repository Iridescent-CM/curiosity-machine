from django.db.models.signals import post_save
from django.dispatch import receiver
from students.models import StudentProfile

@receiver(post_save, sender=StudentProfile)
def auto_approve_non_coppa_students(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw'):
        if instance.birthday and not instance.is_underage():
            instance.user.extra.approved = True
            instance.user.extra.save(update_fields=['approved'])
