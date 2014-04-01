from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from challenges.models import Challenge, Progress
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_student

# refactor input into decorators
@login_required
@mentor_or_current_student
@require_http_methods(["POST",])
def comments(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)

    form = CommentForm(data=request.POST) 
    if form.is_valid():
        text = form.cleaned_data['text']
        comment = Comment()
        comment.user = request.user
        comment.text = text
        comment.challenge_progress = progress
        comment.save()

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username,}))
