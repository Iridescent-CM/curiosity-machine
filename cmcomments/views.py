from curiositymachine.shortcuts import get_object_or_404, json_response
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from challenges.models import Challenge, Progress, Stage, Example
from django.contrib import messages
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_user, mentor_only
from videos.models import Video
from images.models import Image
from .utils import create_comment, StageDoesNotExist
import django_rq

@require_POST
@login_required
@mentor_or_current_user
def comments(request, challenge_id, username, stage, fmt='html'):
    challenge = get_object_or_404(Challenge, id=challenge_id, format=fmt)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username, format=fmt)

    try:
        (success, msgs) = create_comment(challenge=challenge, progress=progress, username=username, stage=stage, data=request.POST, user=request.user)
    except StageDoesNotExist as e:
        from curiositymachine.middleware import ViewException
        raise ViewException(format, str(e), 404)
    redirect = reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username})
    if fmt == 'html':
        if success:
            messages.success(request, "".join(msgs))
        else:
            messages.error(request, "\n".join(msgs))
        return HttpResponseRedirect(redirect)
    else:
        return json_response(success, msgs, redirect=redirect)

# Any POST to this features a student's progress in the "see what other kids built" section on the inspiration page.
# Only one comment from a student for a specific challenge can be featured at a time; multiple POSTs will override previous selections.
# This only really makes sense if the comment has either an image or a video, but there's nothing stopping a forged POST request for a comment without either of those.
@require_http_methods(["POST", "DELETE"])
@mentor_only
def feature_as_example(request, challenge_id, username, stage, comment_id): # "stage" is only used for the redirect
    progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)
    comment = get_object_or_404(progress.comments, id=comment_id)

    if request.method == "POST":
        if Example.objects.filter(progress=progress).exists():
            Example.objects.filter(progress=progress).delete()
            messages.success(request, "{}'s previously featured media was replaced.".format(progress.student))
        else:
            messages.success(request, "{}'s uploaded media was featured on the inspiration page.".format(progress.student))
        Example.objects.create(challenge=progress.challenge, progress=progress, image=comment.image, video=comment.video)
    elif request.method == "DELETE":
        Example.objects.filter(progress=progress).delete()
        messages.error(request, "{}'s previously featured example was un-featured.".format(progress.student))

    return HttpResponse(status=204)
