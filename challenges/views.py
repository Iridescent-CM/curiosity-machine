from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.timezone import now
from django.conf import settings
from .models import Challenge, Progress, Theme, Stage, Example, Favorite, Filter
from cmcomments.forms import CommentForm
from cmcomments.models import Comment
from curiositymachine.decorators import current_user_or_approved_viewer, mentor_only
from curiositymachine.exceptions import LoginRequired
from videos.models import Video
from images.models import Image
from .utils import get_stage_for_progress
from .forms import MaterialsForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator

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
    challenges = challenges.filter(draft=False).select_related('image')

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
    return not (request.user.is_authenticated() or challenge.public)

class InspirationAnonymousPreview(TemplateView):
    template_name = "challenges/edp/preview/inspiration_anonymous.html"

    def get_context_data(self, **kwargs):
        context = super(InspirationAnonymousPreview, self).get_context_data(**kwargs)

        challenge = get_object_or_404(Challenge, id=kwargs.get('challenge_id'))

        context['challenge'] = challenge
        return context

class InspirationUserView(InspirationAnonymousPreview):
    template_name = None
    template_dir = None

    def get_context_data(self, **kwargs):
        context = super(InspirationUserView, self).get_context_data(**kwargs)
        context['examples'] = Example.objects.for_gallery_preview(challenge=context['challenge'])
        return context

    # FIXME: this goes away after #876, when role can be checked directly
    def get_user_role(self):
        if self.request.user.profile.is_student:
            return 'student'
        else:
            return 'none'

    def get_template_names(self):
        return [
            "challenges/edp/%s/%s/inspiration.html" % (self.template_dir, self.get_user_role()),
            "challenges/edp/%s/inspiration_user.html" % self.template_dir
        ]

class InspirationUserPreview(InspirationUserView):
    template_dir = 'preview'

class InspirationUserProgress(InspirationUserView):
    template_dir = 'progress'

    @method_decorator(current_user_or_approved_viewer)
    def dispatch(self, request, *args, **kwargs):
        return super(InspirationUserProgress, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InspirationUserProgress, self).get_context_data(**kwargs)
        context['progress'] = get_object_or_404(
            Progress,
            challenge_id = kwargs.get('challenge_id'),
            student__username = kwargs.get('username')
        )
        return context

class InspirationStudentPreview(InspirationUserPreview):

    def get(self, request, *args, **kwargs):
        username = self.request.user.username
        challenge_id = kwargs.get('challenge_id')
        if Progress.objects.filter(
            challenge=challenge_id,
            student__username=username
        ).exists():
            return HttpResponseRedirect(reverse('challenges:inspiration_progress', kwargs={
                'challenge_id': challenge_id,
                'username': username
            }))
        else:
            return super(InspirationStudentPreview, self).get(request, *args, **kwargs)

class InspirationStudentProgress(InspirationUserProgress):
    pass

class ViewDispatch(View):

    @staticmethod
    def select_view_class(user):
        raise NotImplementedError("Subclass must implement select_view_class(user)")

    def dispatch(self, request, *args, **kwargs):
        viewClass = self.select_view_class(request.user)
        return viewClass.as_view()(request, *args, **kwargs)

class InspirationPreviewDispatch(ViewDispatch):

    @staticmethod
    def select_view_class(user):
        if user.is_authenticated():
            if user.profile.is_student:
                return InspirationStudentPreview
            else:
                return InspirationUserPreview
        else:
            return InspirationAnonymousPreview

class InspirationProgressDispatch(ViewDispatch):
    
    @staticmethod
    def select_view_class(user):
        if user.is_authenticated():
            if user.profile.is_student:
                return InspirationStudentProgress
            else:
                return InspirationUserProgress
        else:
            raise PermissionDenied()

def preview_plan(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    return render(request, 'challenges/preview/plan.html', {
        'challenge': challenge,
        'comment_form': CommentForm(),
    })

def preview_build(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

    return render(request, 'challenges/preview/build.html', {
        'challenge': challenge,
        'comment_form': CommentForm(),
    })

def preview_reflect(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if require_login_for(request, challenge):
        raise LoginRequired()

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

    stageToShow = get_stage_for_progress(progress)
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

    if stageToShow == Stage.test:
        stageToShow = Stage.build
    elif stageToShow == Stage.inspiration:
        return render(request, 'challenges/progress/inspiration.html', {
            'challenge': challenge,
            'progress': progress,
            'examples': Example.objects.for_gallery_preview(challenge=challenge),
        })

    progress.get_unread_comments_for_user(request.user).update(read=True)
    return render(request, "challenges/progress/%s.html" % stageToShow.name, {
        'challenge': challenge,
        'progress': progress,
        'comment_form': CommentForm(),
        'comments': progress.comments.all(),
        'materials_form': MaterialsForm(progress=progress)
    })

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

class ExamplesView(View):
    def get(self, request, challenge_id=None, *args, **kwargs):
        challenge = get_object_or_404(Challenge, id=challenge_id)
        if require_login_for(request, challenge):
            raise LoginRequired()

        if request.user.is_authenticated():
            progress = Progress.objects.filter(challenge_id=challenge_id, student=request.user).first()
            examples = Example.objects.for_gallery(challenge=challenge, user=request.user)
            user_example = examples.filter(progress=progress).first()
        else:
            progress = None
            examples = Example.objects.for_gallery(challenge=challenge)
            user_example = None

        page = request.GET.get('page')
        paginator = Paginator(examples, settings.DEFAULT_PER_PAGE)
        try:
            examples = paginator.page(page)
        except PageNotAnInteger:
            examples = paginator.page(1)
        except EmptyPage:
            examples = paginator.page(paginator.num_pages)

        return render(request, 'challenges/examples/examples.html', {
            'examples': examples,
            'challenge': challenge,
            'progress': progress,
            'user_example': user_example,
        })

    @method_decorator(login_required)
    def post(self, request, challenge_id=None, *args, **kwargs):
        challenge = get_object_or_404(Challenge, id=challenge_id)
        progress = Progress.objects.filter(challenge_id=challenge_id, student=request.user).first()
        image = get_object_or_404(Image, id=request.POST.get('example'))

        if not image.comments.filter(user=request.user, challenge_progress=progress).exists():
            raise Http404("Image not found for this challenge")
        if Example.objects.from_progress(progress=progress).status(approved=True, pending=True).exists():
            return HttpResponse(status=409, reason="Example already exists")
        example = Example(challenge=challenge, progress=progress, image=image)
        example.save()
        return HttpResponseRedirect(reverse('challenges:examples', kwargs={
            'challenge_id': challenge.id,
        }))

class ExamplesDeleteView(View):
    @method_decorator(login_required)
    def post(self, request, challenge_id=None, *args, **kwargs):
        example = get_object_or_404(Example, id=request.POST.get('example-id'))
        if example.progress.student != request.user:
            raise Http404()
        example.approved=False
        example.save()
        return HttpResponseRedirect(reverse('challenges:examples', kwargs={
            'challenge_id': challenge_id,
        }))
