from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from curiositymachine.decorators import mentor_only
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from .models import Module, Comment
from .forms import CommentForm
from videos.models import Video
from images.models import Image

@login_required
@mentor_only
def module(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # if the user is not approved, only show that user's thread
    if not request.user.profile.approved:
        threads = module.comments.filter(user=request.user, thread__isnull=True)
    # if the user is already approved, go ahead and show all threads that belong to unfinished (plus threads that belong to self)
    else:
        threads = module.comments.exclude(user__in=module.mentors_done.all()).filter(thread__isnull=True) | module.comments.filter(user=request.user, thread__isnull=True)

    # no need to serve a 403 to users who somehow cheat and skip ahead, but don't show the form for creating a new thread either
    # otherwise, show the form if you are not approved and you have not already started a thread on this module
    # no exception is made for admins who are not mentors here; if they wish to leave comments they must mark themselves as mentors
    show_thread_form = module.is_accessible_by_mentor(request.user) and not threads and not request.user.profile.approved

    return render(request, "training.html", {"module": module, "threads": threads, "form": CommentForm(),
                  "show_thread_form": show_thread_form, "finished": module.is_finished_by_mentor(request.user),})

@require_POST
@login_required
@mentor_only
def comments(request, module_id, thread_id=None):
    module = get_object_or_404(Module, id=module_id)
    thread = get_object_or_404(module.comments, id=thread_id, thread__isnull=True) if thread_id else None # if thread_id is specified, an invalid thread_id (top-level-comment id) is a 404, but passing in no thread_id at all is legal

    form = CommentForm(data=request.POST)
    if form.is_valid():
        video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
        image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
        Comment.objects.create(user=request.user, text=form.cleaned_data['text'], module=module, thread=thread, image=image, video=video)

    return HttpResponseRedirect(reverse('training:module', args=[str(module_id),]))

@require_POST
@login_required
@permission_required('profiles.change_profile', raise_exception=True)
def approve_module_progress(request, module_id, username):
    module = get_object_or_404(Module, id=module_id)
    mentor = get_object_or_404(User, username=username, profile__is_mentor=True)

    module.mark_mentor_as_done(mentor)
    if User.objects.get(id=mentor.id).profile.approved:
        messages.success(request, 'Mentor {} has completed the final module and is now approved.'.format(mentor.username))
    else:
        messages.success(request, 'Mentor {} has completed module {}.'.format(mentor.username, module.title))

    return HttpResponseRedirect(reverse('training:module', args=[str(module_id),]))
