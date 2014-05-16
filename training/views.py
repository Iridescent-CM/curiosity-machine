from django.shortcuts import render, get_object_or_404
from curiositymachine.decorators import mentor_only
from .models import Module

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
