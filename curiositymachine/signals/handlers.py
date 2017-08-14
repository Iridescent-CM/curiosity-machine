from curiositymachine import signals
from django.dispatch import receiver
from notifications.signals import notify

@receiver(signals.posted_comment)
def create_comment_notification(sender, **kwargs):
    comment = kwargs['comment']
    progress = comment.challenge_progress

    recipients = [progress.student]
    if progress.mentor:
        recipients.append(progress.mentor)
    recipients.remove(sender)

    for recipient in recipients:
        notify.send(sender, recipient=recipient, verb="posted", action_object=comment, target=progress)