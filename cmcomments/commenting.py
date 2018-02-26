from .models import *
from challenges.progressing import Progressing

class Commenting:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def comment(self, commit=True):
        comment = Comment(**self.kwargs)
        if commit:
            comment.save()

        Progressing(progress=comment.challenge_progress).on_comment(comment)

        return comment
