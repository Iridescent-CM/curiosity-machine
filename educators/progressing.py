from challenges.progressing import BaseActor
from notifications.signals import notify

class ProgressEducator(BaseActor):

    def on_progress_complete(self, progress):
        notify.send(progress.owner, recipient=self.user, verb="completed", action_object=progress)

    def on_comment_posted(self, progress, comment):
        pass # can't happen, yet

    def on_comment_received(self, progress, comment):
        notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)
