from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, HttpResponse
from curiositymachine.decorators import mentor_only
from .models import Module, Comment
from .forms import CommentForm

@login_required
@mentor_only
def module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    # if the user is not approved, only show that user's thread
    if not request.user.profile.approved:
        threads = module.comments.filter(user=request.user, thread__isnull=True)
    # if the user is already approved, go ahead and show all threads that belong to non-approved users
    else:
        threads = module.comments.filter(user__profile__approved=False, thread__isnull=True)
    return render(request, "training.html", {"module": module, "threads": threads})

@require_POST
@login_required
@mentor_only
def comments(request, module_id, thread_id=None):
    module = get_object_or_404(Module, id=module_id)
    thread = get_object_or_404(module.comments, id=thread_id, thread__isnull=True) if thread_id else None # if thread_id is specified, an invalid thread_id (top-level-comment id) is a 404, but passing in no thread_id at all is legal

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = Comment(user=request.user, text=form.cleaned_data['text'], module=module, thread=thread)
        comment.save()

    return HttpResponse(status=204)
