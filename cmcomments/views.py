from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from challenges.models import Challenge, Progress
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_student
from videos.models import Video
from images.models import Image
import django_rq

# refactor input into decorators
@login_required
@mentor_or_current_student
def comments(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
        image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
        stage = request.POST['stage']
        if stage == 'plan':
            comment_stage = Comment.PLAN
        elif stage == 'build':
            comment_stage = Comment.BUILD
        elif stage == 'test':
            comment_stage = Comment.TEST
            stage = 'build' # redirect to the build page
        comment = Comment(user=request.user, text=form.cleaned_data['text'], challenge_progress=progress, image=image, video=video, stage=comment_stage)
        comment.save()
    #TODO: add some way to handle form.errors, for instance converting it into a JSON API

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username, 'stage': stage}))
