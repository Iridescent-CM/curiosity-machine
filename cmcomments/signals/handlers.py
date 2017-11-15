from django.db.models.signals import post_save
from django.dispatch import receiver
from challenges.models import Stage
from cmcomments.models import Comment
from curiositymachine import signals

@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    if created:
        comment = instance

        if comment.user.extra.is_student and comment.is_first_reflect_post():
            signals.progress_considered_complete.send(sender=comment.user, progress=comment.challenge_progress)
        else:
            signals.posted_comment.send(sender=comment.user, comment=comment)

@receiver(post_save, sender=Comment)
def check_if_first_project(sender, instance, created, **kwargs):
    comment = instance
    if created and comment.challenge_progress.is_first_project() and comment.is_first_post():
        signals.started_first_project.send(sender=comment.user, progress=comment.challenge_progress)
