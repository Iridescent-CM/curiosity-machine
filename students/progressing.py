from challenges.models import Stage
from challenges.progressing import BaseActor
from cmemails import send
from cmemails.mandrill import url_for_template
from django.urls import reverse
from notifications.signals import notify

class ProgressOwner(BaseActor):
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on_progress_complete(self, progress=None):
        path = reverse('challenges:examples', kwargs={
            "challenge_id": progress.challenge.id
        })
        send(template_name='student-completed-project', to=progress.owner, merge_vars={
            "studentname": progress.owner.username,
            "challengename": progress.challenge.name,
            "inspiration_url": url_for_template(path)
        })

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)

        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": progress.owner.username,
            "stage": Stage(comment.stage).name
        })
        send(template_name='student-mentor-feedback', to=progress.owner, merge_vars={
            "studentname": progress.owner.username,
            "button_url": url_for_template(path)
        })
