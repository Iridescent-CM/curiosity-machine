from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
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

    # no need to serve a 403 to users who somehow cheat and skip ahead, but don't show the form for creating a new thread either
    # otherwise, show the form if you are not approved and you have not already started a thread on this module
    show_thread_form = module.is_accessible_by_mentor(request.user) and not threads and not request.user.profile.approved

    return render(request, "training.html", {"module": module, "threads": threads, "form": CommentForm(), "show_thread_form": show_thread_form,})

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

    return HttpResponseRedirect(reverse('training:module', args=[str(module_id),]))
