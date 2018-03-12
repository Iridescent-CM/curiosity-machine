from cmemails import send
from cmemails.mandrill import url_for_template
from django.contrib.auth import get_user_model
from profiles.models import load_from_role_app
from .models import *

class BaseActor:
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _is_author(self, comment):
        return self.user == comment.user

    def on_comment(self, progress, comment):
        if self._is_author(comment):
            self.on_comment_posted(progress, comment)
        else:
            self.on_comment_received(progress, comment)

    def on_progress_complete(self, progress):
        raise NotImplementedError('Subclasses of BaseActor must implement this')

    def on_comment_posted(self, progress, comment):
        raise NotImplementedError('Subclasses of BaseActor must implement this')

    def on_comment_received(self, progress, comment):
        raise NotImplementedError('Subclasses of BaseActor must implement this')

class NoopActor(BaseActor):
    def on_progress_complete(self, progress):
        pass

    def on_comment_posted(self, progress, comment):
        pass

    def on_comment_received(self, progress, comment):
        pass

def wrap_as_actor(classname, wrapped_user, defaultclass=NoopActor, **kwargs):
    _class = load_from_role_app(wrapped_user.extra.role, "progressing", classname)
    if _class:
        return _class(wrapped_user, **kwargs)
    else:
        return defaultclass(wrapped_user, **kwargs)

class ProgressEducators:
    def __init__(self, progress, educators=None, *args, **kwargs):
        self.progress = progress
        if educators == None:
            self.educators = []
            educators = get_user_model().objects.none()
            for membership in self.progress.owner.membership_set.filter(is_active=True, challenges=self.progress.challenge):
                for educator in membership.educators:
                    self.educators.append(wrap_as_actor("ProgressEducator", educator, membership=membership))
        else:
            self.educators = educators

    def on_progress_complete(self, progress):
        for educator in self.educators:
            educator.on_progress_complete(progress)

    def on_comment(self, progress, comment):
        for educator in self.educators:
            educator.on_comment(progress, comment)

class Progressing:
    def __init__(self, *args, **kwargs):
        self.progress = kwargs.pop('progress')
        self.owner = kwargs.pop('owner', wrap_as_actor("ProgressOwner", self.progress.owner))
        if self.progress.mentor:
            self.mentor = kwargs.pop('mentor', wrap_as_actor("ProgressMentor", self.progress.mentor))
        else:
            self.mentor = NoopActor()
        self.educators = kwargs.pop('educators', ProgressEducators(self.progress))

    def completes_progress(self, comment):
        return (
            Stage(comment.stage) == Stage.reflect
            and self.progress.comments.filter(
                user=self.progress.owner,
                stage=Stage.reflect.value
            ).count() == 1
        )

    def on_comment(self, comment):
        actors = [self.owner, self.mentor, self.educators]
        progress = self.progress

        if self.completes_progress(comment):
            for actor in actors:
                actor.on_progress_complete(progress=progress)
        else:
            for actor in actors:
                actor.on_comment(progress, comment)
