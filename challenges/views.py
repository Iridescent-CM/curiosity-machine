from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Challenge, Progress

def challenges(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges,})

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        # any POST to this endpoint starts the project, creating a Progress object and adding you to the challenge
        Progress.objects.create(challenge=challenge, student=request.user)
        return HttpResponseRedirect('')
    try:
        progress = Progress.objects.get(challenge=challenge, student=request.user)
        return render(request, 'challenge_in_progress.html', {'challenge': challenge, 'progress': progress})
    except Progress.DoesNotExist:
        return render(request, 'challenge.html', {'challenge': challenge,})
