from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Challenge, Progress
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_student

def challenges(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges,})

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        # any POST to this endpoint starts the project, creating a Progress object and adding you to the challenge
        Progress.objects.create(challenge=challenge, student=request.user)
        return HttpResponseRedirect('')
    if Progress.objects.filter(challenge=challenge, student=request.user).exists():
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': request.user.username,}))
    else:
        return render(request, 'challenge.html', {'challenge': challenge,})

# refactor input into decorators
@login_required
@mentor_or_current_student
def challenge_progress(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)

    return render(request, 'challenge_in_progress.html', {'challenge': challenge, 'progress': progress, 'comment_form': CommentForm()})
