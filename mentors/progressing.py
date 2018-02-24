from challenges.progressing import BaseActor
from challenges.models import Stage
from cmemails import send
from cmemails.mandrill import url_for_template
from django.urls import reverse
from notifications.signals import notify

class ProgressMentor(BaseActor):
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on_progress_complete(self, progress=None):
        if self.user:
            path = reverse('challenges:challenge_progress', kwargs={
                "challenge_id": progress.challenge.id,
                "username": progress.owner.username
            })
            send(template_name='mentor-student-completed-project', to=self.user, merge_vars={
                "studentname": progress.owner.username,
                "progress_url": url_for_template(path),
            })

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        if self.user:
            notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)

            path = reverse('challenges:challenge_progress', kwargs={
                "challenge_id": progress.challenge.id,
                "username": progress.owner.username,
                "stage": Stage(comment.stage).name
            })
            send(template_name='mentor-student-responded-to-feedback', to=progress.mentor, merge_vars={
                "studentname": progress.owner.username,
                "progress_url": url_for_template(path)
            })

