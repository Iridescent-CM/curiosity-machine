from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from challenges.models import Challenge, Progress, Stage, Example
from django.contrib import messages
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from videos.models import Video
from images.models import Image


def create_comment(user, challenge, progress, username, stage, data):
    try:
        stage = Stage[stage]
    except KeyError:
        raise Http404

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