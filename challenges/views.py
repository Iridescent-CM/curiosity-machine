from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import django_rq

from .models import Challenge, Progress, Theme
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_student
from videos.models import Video
from .forms import ChallengeVideoForm

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
        try:
            Progress.objects.create(challenge=challenge, student=request.user)
            return HttpResponseRedirect('')
        except (ValueError, ValidationError):
            return HttpResponse("You must be logged in as a student to start a challenge.", status=403)
    if request.user.is_authenticated() and Progress.objects.filter(challenge=challenge, student=request.user).exists():
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': request.user.username,}))
    else:
        return render(request, 'challenge.html', {'challenge': challenge, 'video_form': ChallengeVideoForm()})

@login_required
@mentor_or_current_student
def challenge_progress(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)
    
    try:
        progress.get_unread_comments_for_user(request.user).update(read=True)
    except AttributeError:
        pass

    return render(request, 'challenge_in_progress.html', {'challenge': challenge, 'progress': progress, 'comment_form': CommentForm()})
