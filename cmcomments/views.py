from django.shortcuts import render, get_object_or_404
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
import django_rq

@require_POST
@login_required
@mentor_or_current_user
def comments(request, challenge_id, username, stage):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)
    try:
        stage = Stage[stage]
    except KeyError:
        raise Http404

    form = CommentForm(data=request.POST)
    if form.is_valid():
        video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
        image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
        comment = Comment(user=request.user, text=form.cleaned_data['text'], challenge_progress=progress, image=image, video=video, stage=stage.value, question_text=form.cleaned_data['question_text'])
        profile = request.user.profile
        if stage.value != Stage.reflect.value:
            if profile.is_mentor:
                progress.email_mentor_responded()
            elif progress.mentor:
                progress.email_student_responded()
        comment.save()
    #TODO: add some way to handle form.errors, for instance converting it into a JSON API

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username}))

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

@require_http_methods(["POST", "DELETE"])
def delete_comment(request, challenge_id, username, comment_id, stage=None): # "stage" is only used for the redirect
    progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)
    comment = get_object_or_404(progress.comments, id=comment_id)
    if request.method == "DELETE":
        comment.delete()
        messages.success(request, "{}'s comment deleted.".format(progress.student))

    return HttpResponse(status=204)

@require_http_methods(["POST"])
def edit_comment(request, challenge_id, username, comment_id, stage=None): # "stage" is only used for the redirect
    form = CommentForm(data=request.POST)
    if form.is_valid():
        progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)
        comment = get_object_or_404(progress.comments, id=comment_id)
        comment.text = form.cleaned_data['text']
        comment.save()
        messages.success(request, "{}'s comment edited.".format(progress.student))

    return HttpResponse(status=204)
