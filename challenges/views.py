from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import django_rq

from .models import Challenge, Progress, Theme, Stage
from cmcomments.forms import CommentForm
from cmcomments.models import Comment
from curiositymachine.decorators import mentor_or_current_student
from videos.models import Video
from .forms import ChallengeVideoForm
from .utils import get_stage_for_progress

def challenges(request):
    challenges = Challenge.objects.all()
    theme = request.GET.get('theme')
    if theme:
        challenges = challenges.filter(theme__name=theme)
    themes = Theme.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges, 'themes': themes, 'theme': theme})

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        # any POST to this endpoint starts the project, creating a Progress object and adding you to the challenge
        if not Progress.objects.filter(challenge=challenge, student=request.user).exists():
            try:
                Progress.objects.create(challenge=challenge, student=request.user)
            except (ValueError, ValidationError):
                return HttpResponse("You must be logged in as a student to start a challenge.", status=403)
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': request.user.username,}))
    else:
        return render(request, 'challenge.html', {'challenge': challenge, 'video_form': ChallengeVideoForm()})

@login_required
@mentor_or_current_student
def challenge_progress(request, challenge_id, username, stage=None): # stage will be one of None, "plan", "build". "build" encompasses the reflection stage
    challenge = get_object_or_404(Challenge, id=challenge_id)

    try:
        progress = Progress.objects.get(challenge=challenge, student__username=username)
    except Progress.DoesNotExist:
        # if user hasn't started the challenge, redirect to Inspiration page
        return HttpResponseRedirect(reverse('challenges:challenge', kwargs={'challenge_id': challenge.id,}))

    try:
        stage = Stage[stage]
    except KeyError: # if stage is None or any invalid input, redirect to the stage with most recent progress
        stage = get_stage_for_progress(progress)
        stage_string = stage.name if stage == Stage.plan else Stage.build.name # there may be other valid stages, but right now we only support plan or build as redirect destinations
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username, 'stage': stage_string}))

    if stage in [Stage.build, Stage.test]:
        comments = Comment.objects.filter(challenge_progress=progress, stage__in=[Stage.build, Stage.test])
    else:
        comments = Comment.objects.filter(challenge_progress=progress, stage=stage)

    progress.get_unread_comments_for_user(request.user).update(read=True)

    return render(request, "challenge_plan.html" if stage == Stage.plan else "challenge_build.html",
                  {'challenge': challenge, 'progress': progress, 'comment_form': CommentForm(), 'comments': comments})
