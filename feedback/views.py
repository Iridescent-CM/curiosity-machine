from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from curiositymachine.decorators import mentor_or_current_user
from challenges.models import Challenge, Progress, Stage
from cmcomments.commenting import Commenting
from .forms import FeedbackForm

@require_POST
@login_required
@mentor_or_current_user
def make_comment(request, challenge_id, username, stage):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, owner__username=username)
    try:
        stage = Stage[stage]
    except KeyError:
        raise Http404
    feedback = challenge.feedback_set.first()
    form = FeedbackForm(request.POST, model=feedback)
    if form.is_valid():
        result = form.get_result(request.user, challenge=challenge)
        result.save()
    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username})
        )
    )
