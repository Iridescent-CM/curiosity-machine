from django.shortcuts import render, get_object_or_404
from .models import Challenge

def challenges(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges,})

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request, 'challenge.html', {'challenge': challenge,})
