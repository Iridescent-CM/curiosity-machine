from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from challenges.models import Challenge, Progress, Stage, Example
from django.contrib import messages
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from curiositymachine.decorators import current_user_or_approved_viewer
from videos.models import Video
from images.models import Image
import django_rq
import logging

logger = logging.getLogger(__name__)

@require_POST
@login_required
@current_user_or_approved_viewer
def comments(request, challenge_id, username, stage):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, owner__username=username)
    try:
        stage = Stage[stage]
    except KeyError:
        raise Http404

    form = CommentForm(data=request.POST)
    if form.is_valid():
        media = form.cleaned_data['visual_media']
        video = Video.from_source_with_job(media['url']) if media and media['mimetype'].startswith('video') else None
        image = Image.from_source_with_job(media['url']) if media and media['mimetype'].startswith('image') else None
        if 'stepSelector' in request.POST:
            try:
                stage = Stage[request.POST['stepSelector']]
            except KeyError:
                raise Http404
        Commenting(
            user=request.user,
            text=form.cleaned_data['text'],
            challenge_progress=progress,
            image=image,
            video=video,
            stage=stage.value,
            question_text=form.cleaned_data['question_text']
        ).comment()
    else:
        logger.info("Invalid comment: " + form.errors.as_json())

    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username})
        )
    )
