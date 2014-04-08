from django.shortcuts import get_object_or_404
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
        comment = Comment(user=request.user, text=form.cleaned_data['text'], challenge_progress=progress, image=form.cleaned_data['filepicker_url'])
        comment.save()
    #TODO: add some way to handle form.errors, for instance converting it into a JSON API

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username,}))
