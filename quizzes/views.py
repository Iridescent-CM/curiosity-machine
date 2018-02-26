from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from curiositymachine.decorators import mentor_or_current_user
from challenges.models import Challenge, Progress, Stage
from cmcomments.commenting import Commenting
from .forms import QuizForm

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
    quiz = challenge.quiz_set.first()
    form = QuizForm(request.POST, model=quiz)
    if form.is_valid():
        result = form.get_result(request.user)
        result.save()
        Commenting(
            user=request.user,
            text=result.comment_text,
            challenge_progress=progress,
            stage=stage.value,
            question_text="Reflection quiz"
        ).comment()
    else:
        # TODO: do better
        messages.error(request, 'Please answer all questions')
    # TODO: maybe don't redirect, render directly with form and potential errors
    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username})
        )
    )
