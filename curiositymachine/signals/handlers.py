from curiositymachine import signals
from django.dispatch import receiver
from notifications.signals import notify

def recipients_for(comment, sender):
    progress = comment.challenge_progress
    if sender != progress.student:
        return [progress.student]
    elif progress.mentor:
        return [progress.mentor]
    else:
        return []

@receiver(signals.posted_comment)
def create_comment_notification(sender, **kwargs):
    comment = kwargs['comment']
    progress = comment.challenge_progress
    for recipient in recipients_for(comment, sender):
        notify.send(sender, recipient=recipient, verb="posted", action_object=comment, target=progress)