from django.shortcuts import render, get_object_or_404
from challenges.models import Challenge, Progress

# refactor input into decorators
# need security on this that only lets a student view his/her own progress
def comments(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)

    if request.method == "POST":
        print(request.POST)
    from django.http import HttpResponse
    return HttpResponse("comments!")