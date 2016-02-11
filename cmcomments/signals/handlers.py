from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Stage
from cmcomments.models import Comment
from cmemails import deliver_email
from curiositymachine import signals

def is_first_reflect_post(comment):
    return comment.stage == Stage.reflect.value and Comment.objects.filter(
        challenge_progress=comment.challenge_progress,
        user=comment.user,
        stage=Stage.reflect.value
    ).count() == 1

@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    if created:
        comment = instance

        if is_first_reflect_post(comment):
            signals.progress_considered_complete.send(sender=comment.user, progress=comment.challenge_progress)
        else:
            signals.posted_comment.send(sender=comment.user, comment=comment)
