from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.timezone import now
import django_rq

from .models import Challenge, Progress, Theme, Stage, Example, Favorite, Filter
from cmcomments.forms import CommentForm
from cmcomments.models import Comment
from curiositymachine.decorators import mentor_or_current_user, mentor_only
from videos.models import Video
from .utils import get_stage_for_progress
from .forms import MaterialsForm
from django.core.exceptions import PermissionDenied

def challenges(request):
    challenges = Challenge.objects.filter(draft=False)
    theme = request.GET.get('theme')
    theme_id = request.GET.get('theme_id')
    filters = Filter.objects.filter(visible=True)
    if theme:
        challenges = challenges.filter(theme__name=theme)
    themes = Theme.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges, 'themes': themes, 'theme': theme, 'theme_id': theme_id, 'filters': filters})

def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        # any POST to this endpoint starts the project, creating a Progress object and adding you to the challenge
        if not Progress.objects.filter(challenge=challenge, student=request.user).exists():
            try:
                Progress.objects.create(challenge=challenge, student=request.user)
            except (ValueError, ValidationError):
                raise PermissionDenied
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': request.user.username,}))
    else:
        return render(request, 'challenge.html', {'challenge': challenge, 'examples': Example.objects.filter(challenge=challenge),})

def plan_guest(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request, 'challenge_plan_guest.html', {'challenge': challenge})

def build_guest(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request, 'challenge_build_guest.html', {'challenge': challenge})

@login_required
@mentor_or_current_user
def challenge_progress(request, challenge_id, username, stage=None): # stage will be one of None, "plan", "build". "build" encompasses the reflection stage
    challenge = get_object_or_404(Challenge, id=challenge_id)

    try:
        progress = Progress.objects.get(challenge=challenge, student__username=username)
    except Progress.DoesNotExist:
        # if user hasn't started the challenge, redirect to Inspiration page
        return HttpResponseRedirect(reverse('challenges:challenge', kwargs={'challenge_id': challenge.id,}))

    try:
        stage = Stage[stage]
    except KeyError: # if stage is None or any invalid input, redirect to the stage with most recent progress
        stage = get_stage_for_progress(progress)
        stage_string = stage.name if stage == Stage.plan else Stage.build.name # there may be other valid stages, but right now we only support plan or build as redirect destinations
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username, 'stage': stage_string}))

    if stage == Stage.inspiration:
        return render(request, 'challenge.html', {'challenge': challenge, 'progress': progress, 'examples': Example.objects.filter(challenge=challenge),})
    elif stage in [Stage.build, Stage.test, Stage.reflect]:
        comments = progress.comments.filter(stage__in=[Stage.build.value, Stage.test.value, Stage.reflect.value])
    else:
        comments = progress.comments.filter(stage=stage.value)

    progress.get_unread_comments_for_user(request.user).update(read=True)

    return render(request, "challenge_plan.html" if stage == Stage.plan else "challenge_build.html",
                  {'challenge': challenge, 'progress': progress, 'comment_form': CommentForm(), 'comments': comments, 'materials_form': MaterialsForm(progress=progress)})

# Any POST to this by the assigned mentor moves a challenge progress into the reflect stage (marks approve=True); any DELETE reverses that
@require_http_methods(["POST", "DELETE"])
@login_required
def challenge_progress_approve(request, challenge_id, username):
    progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)

    #Only the mentor assigned to the progress can approve/un-approve it
    if not request.user == progress.mentor:
        raise PermissionDenied

    if request.method == "POST":
        progress.approve()
        messages.success(request, 'Learner was progressed to Reflection')
    elif request.method == "DELETE":
        Progress.objects.filter(id=progress.id).update(approved=None)

    return HttpResponse(status=204)

@mentor_only
def unclaimed_progresses(request):
    progresses = Progress.objects.filter(mentor__isnull=True)

    return render(request, "unclaimed_progresses.html", {"progresses": progresses})

# Any POST to this assigns the current user to a progress as a mentor
# currently there is no security to stop a mentor from claiming a progress already claimed by another mentor by manually POSTing
@require_http_methods(["POST"])
@mentor_only
def claim_progress(request, progress_id):
    progress = get_object_or_404(Progress, id=progress_id)

    progress.mentor = request.user
    progress.save(update_fields=["mentor"])

    messages.success(request, 'You have successfully claimed this challenge.')

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': progress.challenge.id, 'username': progress.student.username,}))
    #return HttpResponse(status=204)

# Any POST to this changes the materials list for that progress
@require_http_methods(["POST"])
def change_materials(request, challenge_id, username):
    progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)

    form = MaterialsForm(request.POST, progress=progress)
    if form.is_valid():
        progress._materials_list = form.cleaned_data['materials']
        progress.save(update_fields=["_materials_list"])

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': progress.challenge.id, 'username': progress.student.username, 'stage': 'plan'}))

@login_required
def set_favorite(request, challenge_id, mode='favorite'):
    content_type="application/json"
    user = request.user
    
    challenge = get_object_or_404(Challenge, id=challenge_id)
    try:
        if mode == 'favorite':
            Favorite.objects.create(challenge=challenge, student=request.user)
        elif mode == 'unfavorite':
            favorite = Favorite.objects.filter(challenge=challenge, student=request.user)
            favorite.delete()
    except ValidationError as e:
        return JsonResponse({'success': False, 'errors': e.messages}, content_type=content_type)
    except ValueError as e:
        errors = [str(e)]
        return JsonResponse({'success': False, 'errors': errors}, content_type=content_type)
    return JsonResponse({'success': True, 'message': 'Success'}, content_type=content_type)

@login_required
def favorite_challenges(request):
    favorite_challenges = []
    if request.user.is_authenticated():
        theme_id = request.GET.get('theme_id')
        if theme_id:
            favorite_challenges = Favorite.objects.filter(student=request.user, challenge__theme_id=theme_id)
        else:
            favorite_challenges = Favorite.objects.filter(student=request.user)
    return render(request, 'ajax/favorites.html', {'favorite_challenges': favorite_challenges})


def ajax_challenges(request):
    challenges = Challenge.objects.filter(draft=False)
    theme = request.GET.get('theme')
    if theme:
        challenges = challenges.filter(theme__name=theme)
    return render(request, 'ajax/challenges.html', {'challenges': challenges, 'theme': theme})

def filtered_challenges(request, filter_id):
    theme_id = request.GET.get('theme_id')
    if theme_id:
        challenges = Filter.objects.get(pk=filter_id).challenges.filter(theme__id=theme_id)
    else:
        challenges = Filter.objects.get(pk=filter_id).challenges.all
    return render(request, 'ajax/challenges.html', {'challenges': challenges})
