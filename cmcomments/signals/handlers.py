from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Stage
from cmcomments.models import Comment
from cmemails import deliver_email
from curiositymachine import signals

@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    comment = instance
    progress = comment.challenge_progress
    if created:
        if comment.user.profile.is_mentor:
            signals.mentor.posted_comment.send(sender=comment.user, comment=comment)
        elif comment.user.profile.is_student:
            signals.student.posted_comment.send(sender=comment.user, comment=comment)
