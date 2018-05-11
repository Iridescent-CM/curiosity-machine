from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from curiositymachine.decorators import mentor_or_current_user
from challenges.models import Challenge, Progress, Stage
from cmcomments.commenting import Commenting
from .forms import FeedbackQuestionForm

@require_POST
@login_required
@mentor_or_current_user
def make_comment(request, challenge_id, username, stage):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    try:
        stage = Stage[stage]
    except KeyError:
        raise Http404
    feedback_question = challenge.feedback_question
    form = FeedbackQuestionForm(request.POST, model=feedback_question)
    if form.is_valid():
        feedback_result = form.get_feedback_result(request.user, challenge=challenge)
        feedback_result.save()
    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username})
        )
    )
