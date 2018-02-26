from cmemails import send
from cmemails.mandrill import url_for_template
from profiles.models import load_from_role_app
from .models import *

class BaseActor:
    def __init__(self, user=None, *args, **kwargs):
        self.user = user

    def is_author(self, comment):
        return self.user == comment.user

class NoopActor(BaseActor):
    def on_progress_complete(self, progress):
        pass

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        pass

class Progressing:
    def __init__(self, *args, **kwargs):
        self.progress = kwargs.pop('progress')
        self.owner = kwargs.pop('owner', self.wrap("ProgressOwner", self.progress.owner))
        if self.progress.mentor:
            self.mentor = kwargs.pop('mentor', self.wrap("ProgressMentor", self.progress.mentor))
        else:
            self.mentor = NoopActor()

    def wrap(self, classname, wrapped_user, defaultclass=NoopActor):
        _class = load_from_role_app(wrapped_user.extra.role, "progressing", classname)
        if _class:
            return _class(wrapped_user)
        else:
            return defaultclass(wrapped_user)

    def completes_progress(self, comment):
        return (
            Stage(comment.stage) == Stage.reflect
            and self.progress.comments.filter(
                user=self.progress.owner,
                stage=Stage.reflect.value
            ).count() == 1
        )

    def on_comment(self, comment):
        actors = [self.owner, self.mentor]
        progress = self.progress

        if self.completes_progress(comment):
            for actor in actors:
                actor.on_progress_complete(progress=progress)
        else:
            for actor in actors:
                if actor.is_author(comment):
                    actor.on_comment_posted(progress, comment)
                else:
                    actor.on_comment_received(progress, comment)
