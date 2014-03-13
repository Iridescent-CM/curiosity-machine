from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Challenge

def challenge_inspiration(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)


    template_values = {
        'challenge':challenge,
    }

    return render(request, 'challenge_inspiration.html', template_values)


def challenge_plan(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)


    template_values = {
        'challenge':challenge,
    }

    return render(request, 'challenge_plan.html', template_values)


def challenge_build(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)


    template_values = {
        'challenge':challenge,
    }

    return render(request, 'challenge_build.html', template_values)
