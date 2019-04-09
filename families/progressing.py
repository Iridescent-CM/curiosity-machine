from challenges.models import Stage as ChallengeStage
from challenges.progressing import BaseActor
from cmemails import send
from cmemails.mandrill import url_for_template
from django.urls import reverse
from notifications.signals import notify
from .emailing import Emailing

class ProgressOwner(BaseActor):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.emailer = kwargs.pop('emailer', Emailing(user))

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)

        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": progress.owner.username
        })
        send(template_name='family-account-mentor-feedback', to=progress.owner, merge_vars={
            "username": progress.owner.username,
            "button_url": url_for_template(path)
        })
