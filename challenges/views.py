from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from django.utils.timezone import now
from django.conf import settings
from .models import Challenge, Progress, Theme, Stage, Example, Favorite, Filter
from cmcomments.forms import CommentForm
from cmcomments.models import Comment
from curiositymachine.decorators import current_user_or_approved_viewer, mentor_only
from curiositymachine.middleware import LoginRequired
from videos.models import Video
from .utils import get_stage_for_progress
from .forms import MaterialsForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def challenges(request):
    theme_name = request.GET.get('theme')
    filter_id = request.GET.get('filter_id')
    page = request.GET.get('page')

    title = "All"
    challenges = []
    filt = None

    if (filter_id):
        filt = Filter.objects.get(pk=filter_id)
        challenges = filt.challenges
        title = filt.name
    else:
        challenges = Challenge.objects
    challenges = challenges.filter(draft=False).select_related('image', 'profile')

    filters = Filter.objects.filter(visible=True).prefetch_related('challenges__image')
    themes = Theme.objects.all()
    favorite_ids = set()
    if request.user.is_authenticated():
        favorite_ids = set(Favorite.objects.filter(student=request.user).values_list('challenge__id', flat=True))

    if theme_name:
        challenges = challenges.filter(themes__name=theme_name)
        title = theme_name

    paginator = Paginator(challenges, settings.CHALLENGES_PER_PAGE)
    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        challenges = paginator.page(1)
    except EmptyPage:
        challenges = paginator.page(paginator.num_pages)

    return render(request, 'challenges/new.html', {
        'challenges': challenges,
        'themes': themes,
        'active_theme_name': theme_name,
        'filters': filters,
        'active_filter': filt,
        'favorite_ids': favorite_ids,
        'title': title + " Design Challenges"
    })

@require_POST
def start_building(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if not Progress.objects.filter(challenge=challenge, student=request.user).exists():
        try:
            Progress.objects.create(challenge=challenge, student=request.user)
        except (ValueError, ValidationError):
            raise PermissionDenied
    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={
        'challenge_id': challenge.id,
        'username': request.user.username,
    }))

def require_login_for(request, challenge):
    if settings.FEATURE_FLAGS.get('enable_challenge_preview_restriction'):
        return not (request.user.is_authenticated() or challenge.public)
    return False

def preview_inspiration(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    return render(request, 'challenges/preview/inspiration.html', {
        'challenge': challenge,
        'examples': Example.objects.filter(challenge=challenge),
    })

def preview_plan(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    return render(request, 'challenges/preview/plan.html', {'challenge': challenge})

def preview_build(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    return render(request, 'challenges/preview/build.html', {'challenge': challenge})

def preview_reflect(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    #if not request.user.is_authenticated() or request.user.profile.is_student:
    if False:
        messages.info(request, 'After you build and test, your mentor will approve your challenge to Reflect!')
        return HttpResponseRedirect(request.META.get(
            'HTTP_REFERER',
            reverse('challenges:preview_inspiration', kwargs={
                'challenge_id': challenge_id,
            })
        ))
    else:
        return render(request, 'challenges/preview/reflect.html', {
            'challenge': challenge,
            'comment_form': CommentForm(),
        })

@login_required
@current_user_or_approved_viewer
def redirect_to_stage(request, challenge_id, username):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    try:
        progress = Progress.objects.get(challenge=challenge, student__username=username)
    except Progress.DoesNotExist:
        return HttpResponseRedirect(reverse('challenges:preview_inspiration', kwargs={'challenge_id': challenge.id,}))

    if progress.approved:
        stageToShow = Stage.reflect
    else:
        latestStage = get_stage_for_progress(progress)
        if latestStage == Stage.test:
            stageToShow = Stage.build
        elif latestStage == Stage.reflect and request.user.profile.is_student and not progress.approved:
            stageToShow = Stage.build
        else:
            stageToShow = latestStage
    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={
        'challenge_id': challenge.id,
        'username': username,
        'stage': stageToShow.name
    }))

@login_required
@current_user_or_approved_viewer
def challenge_progress(request, challenge_id, username, stage=None):
    requestedStage = stage
    challenge = get_object_or_404(Challenge, id=challenge_id)

    try:
        progress = Progress.objects.get(challenge=challenge, student__username=username)
    except Progress.DoesNotExist:
        return HttpResponseRedirect(reverse('challenges:preview_inspiration', kwargs={'challenge_id': challenge.id,}))

    try:
        stageToShow = Stage[requestedStage]
    except KeyError:
        raise Http404("Stage does not exist")

    if stageToShow == Stage.inspiration:
        return render(request, 'challenges/progress/inspiration.html', {
            'challenge': challenge,
            'progress': progress,
            'examples': Example.objects.filter(challenge=challenge),
        })
    #elif stageToShow == Stage.reflect and request.user.profile.is_student and not progress.approved:
    #    messages.info(request, 'Not yet! Your mentor needs to approve your challenge for the Reflect stage.')
    #    return HttpResponseRedirect(request.META.get(
    #        'HTTP_REFERER',
    #        reverse('challenges:challenge_progress', kwargs={
    #            'challenge_id': challenge.id,
    #            'username': username,
    #            'stage': Stage.inspiration.name
    #        })
    #    ))

    progress.get_unread_comments_for_user(request.user).update(read=True)
    return render(request, "challenges/progress/%s.html" % stageToShow.name, {
        'challenge': challenge,
        'progress': progress,
        'comment_form': CommentForm(),
        'comments': progress.comments.all(),
        'materials_form': MaterialsForm(progress=progress)
    })

# Any POST to this by the assigned mentor moves a challenge progress into the reflect stage (marks approve=True); any DELETE reverses that
@require_http_methods(["POST"])
@login_required
def challenge_progress_approve(request, challenge_id, username):
    progress = get_object_or_404(Progress, challenge_id=challenge_id, student__username=username)

    #Only the mentor assigned to the progress can approve/un-approve it
    if not request.user == progress.mentor:
        raise PermissionDenied

    if request.POST.get("approve", False):
        progress.approve(approver=request.user)
        messages.success(request, 'Student was moved to Reflect')
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={
            'challenge_id': challenge_id,
            'username': username,
            'stage': Stage.reflect.name
        }))
    else:
        Progress.objects.filter(id=progress.id).update(approved=None)
        return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={
            'challenge_id': challenge_id,
            'username': username,
            'stage': Stage.build.name
        }))

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
            favorite_challenges = Favorite.objects.filter(student=request.user, challenge__themes__id=theme_id)
        else:
            favorite_challenges = Favorite.objects.filter(student=request.user)
    favorite_ids = {favorite.challenge.id for favorite in favorite_challenges}
    return render(request, 'ajax/favorites.html', {
        'favorite_challenges': favorite_challenges,
        'favorites': favorite_ids
    })

def examples(request, challenge_id):
    examples = Example.objects.filter(challenge_id=challenge_id)
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request, 'challenges/examples/examples.html', {
        'examples': examples,
        'challenge': challenge,
    })
