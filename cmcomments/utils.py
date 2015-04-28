from challenges.models import Challenge, Progress, Stage, Example
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from videos.models import Video
from images.models import Image

class StageDoesNotExist(Exception): pass

def create_comment(user, challenge, progress, username, stage, data):
    try:
        stage = Stage[stage]
    except KeyError:
        raise StageDoesNotExist("Invalid stage")

    form = CommentForm(data=data)
    if form.is_valid():
        video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
        image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
        comment = Comment(user=user, text=form.cleaned_data['text'], challenge_progress=progress, image=image, video=video, stage=stage.value, question_text=form.cleaned_data['question_text'])
        profile = user.profile
        if stage.value != Stage.reflect.value:
            if profile.is_mentor:
                progress.email_mentor_responded()
            elif progress.mentor:
                progress.email_student_responded()
        comment.save()
        return (True, ["Successfully created comment"])
    else:
        return (False, map(lambda x: str(x), form.errors.as_data()) )
