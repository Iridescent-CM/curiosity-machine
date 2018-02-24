
class ProgressOwner:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on_progress_complete(self, progress=None):
        pass

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        notify.send(comment.user, recipient=self.user, verb="posted", action_object=comment, target=progress)
