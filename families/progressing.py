from challenges.progressing import BaseActor
from notifications.signals import notify
from .aichallenge import get_stages
from .emailing import Emailing

class ProgressOwner(BaseActor):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.stages = kwargs.pop('stages', get_stages(user))
        self.emailer = kwargs.pop('emailer', Emailing(user))

    def on_progress_complete(self, progress=None):
        for stage in self.stages:
            if stage.is_complete and stage.has_challenge(progress.challenge):
                self.emailer.send_stage_completion_email(stage)

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)

        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": progress.owner.username,
            "stage": Stage(comment.stage).name
        })
        send(template_name='family-account-mentor-feedback', to=progress.owner, merge_vars={
            "username": progress.owner.username,
            "button_url": url_for_template(path)
        })
