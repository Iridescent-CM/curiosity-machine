from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from .models import Challenge, Progress, Theme, Stage, Example, Favorite, Filter
from cmcomments.forms import CommentForm
from curiositymachine.decorators import current_user_or_approved_viewer, mentor_only, student_only
from images.models import Image
from .utils import get_stage_for_progress
from .forms import MaterialsForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from memberships.models import Membership
from memberships.decorators import enforce_membership_challenge_access
from django.db.models import Count
from urllib.parse import quote_plus
from quizzes.forms import QuizForm

def _paginate(qs, page, perPage):
    paginator = Paginator(qs, perPage)
    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)

    return paginated

def _decorate_access(request, challenges):
    accessible = Membership.filter_by_challenge_access(request.user, [c.id for c in challenges])
    for challenge in challenges:
        challenge.accessible = challenge.id in accessible
    return challenges

def _decorate_started(request, challenges):
    if request.user.is_authenticated():
        started_challenges = request.user.challenges.filter(id__in=[c.id for c in challenges])
        for challenge in challenges:
            challenge.started = challenge in started_challenges
    return challenges

def _get_int_or_404(params, key):
    value = params.get(key)
    try:
        value = int(value)
    except ValueError:
        raise Http404
    return value

class FilterSet():
    query_param = None

    def __init__(self, request=None):
        self.request = request
        self.applied = None
        self.active = None

    @property
    def requested(self):
        if not hasattr(self, "query_param"):
            return False
        else:
            return self.query_param in self.request.GET

    def apply(self):
        pass

    def get_template_contexts():
        pass

class UnfilteredChallenges(FilterSet):
    def apply(self):
        self.applied = True
        return "All Design Challenges", Challenge.objects, None

    def get_template_contexts(self):
        return [{
            "text": "All Challenges",
            "full_url": reverse("challenges:challenges") + "#challenges",
            "active": bool(self.applied)
        }]

class MembershipChallenges(FilterSet):
    query_param = "membership"

    def apply(self):
        membership_id = _get_int_or_404(self.request.GET, self.query_param)

        if not self.request.user.is_authenticated():
            return None, None, HttpResponseRedirect('%s?next=%s' % (reverse('login'), quote_plus(self.request.get_full_path())))

        membership = Membership.objects.filter(id=membership_id, members=self.request.user, is_active=True).first()
        if not membership:
            messages.error(self.request, "Oops! You are not part of that membership.")
            return None, None, redirect("challenges:challenges")

        self.applied = membership_id
        return membership.display_name + " Design Challenges", membership.challenges, None

    def get_template_contexts(self):
        user_memberships = []
        if self.request.user.is_authenticated():
            user_memberships = self.request.user.membership_set.filter(is_active=True)

        return [{
            "text": membership.display_name,
            "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, membership.id),
            "active": membership.id == self.applied
        } for membership in user_memberships]

class CoreChallenges(FilterSet):
    query_param = "free"

    def apply(self):
        self.applied = True
        return "Free Design Challenges", Challenge.objects.filter(core=True), None

    def get_template_contexts(self):
        if Challenge.objects.filter(core=True, draft=False).count() > 0:
            return [{
                "text": "Free Challenges",
                "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, 1),
                "active": bool(self.applied)
            }]
        else:
            return []

class FilterChallenges(FilterSet):
    query_param = "filter_id"

    def apply(self):
        filter_id = _get_int_or_404(self.request.GET, self.query_param)
        self.active = get_object_or_404(Filter.objects.filter(visible=True), id=filter_id)

        self.applied = filter_id
        return self.active.name + " Design Challenges", self.active.challenges, None

    def get_template_contexts(self):
        filters = Filter.objects.filter(visible=True).prefetch_related('challenges__image')
        return [{
            "text": f.name,
            "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, f.id),
            "active": f.id == self.applied
        } for f in filters]

class ThemeChallenges(FilterSet):
    query_param = "theme"

    def apply(self):
        theme_name = self.request.GET.get(self.query_param)
        self.applied = theme_name
        return theme_name + " Design Challenges", Challenge.objects.filter(themes__name=theme_name), None

    def get_template_contexts(self):
        return [{
            "text": '<i class="icon %s"></i> %s' % (theme.icon, theme.name),
            "full_url": reverse("challenges:challenges") + "?%s=%s#challenges" % (self.query_param, theme.name),
            "active": theme.name == self.applied
        } for theme in Theme.objects.all()]

def challenges(request):
    filterChallenges = FilterChallenges(request)
    coreChallenges = CoreChallenges(request)
    filtersets = [
        MembershipChallenges(request),
        coreChallenges,
        filterChallenges,
        ThemeChallenges(request)
    ]
    default_filterset = UnfilteredChallenges()
    filterset = next((f for f in filtersets if f.requested), default_filterset)
    title, challenges, response = filterset.apply()
    if response:
        return response

    challenges = challenges.filter(draft=False).select_related('image')

    if request.user.is_authenticated() and not request.user.profile.is_student:
        challenges = challenges.annotate(has_resources=Count('resource'))

    challenges = _decorate_access(request, challenges)

    favorite_ids = set()
    if request.user.is_authenticated():
        favorite_ids = set(Favorite.objects.filter(student=request.user).values_list('challenge__id', flat=True))
        _decorate_started(request, challenges)

    filter_controls = default_filterset.get_template_contexts()
    for filterset in filtersets:
        filter_controls = filter_controls + filterset.get_template_contexts()

    challenges = _paginate(challenges, request.GET.get('page'), settings.CHALLENGES_PER_PAGE)

    header_template = None
    if filterChallenges.active:
        header_template = filterChallenges.active.header_template
    elif coreChallenges.applied:
        header_template = "challenges/filters/free.html"

    return render(request, 'challenges/list.html', {
        'title': title,
        'challenges': challenges,
        'favorite_ids': favorite_ids,
        'filters': filter_controls,
        'header_template': header_template,
    })

@require_POST
@student_only
@enforce_membership_challenge_access
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

class InspirationAnonymousPreview(TemplateView):
    template_name = "challenges/edp/preview/inspiration_anonymous.html"

    def get_context_data(self, **kwargs):
        context = super(InspirationAnonymousPreview, self).get_context_data(**kwargs)

        challenge = get_object_or_404(Challenge, id=kwargs.get('challenge_id'))
        challenge.accessible = bool(Membership.filter_by_challenge_access(self.request.user, [challenge.id]))
        resources = challenge.resource_set.all()

        context['challenge'] = challenge
        context['resources'] = resources
        context['col_width'] = 4 if resources else 6
        context['challenge_difficulties'] = Challenge.DIFFICULTY_LEVELS
        return context

class InspirationUserView(InspirationAnonymousPreview):
    template_name = None
    template_dir = None

    def get_context_data(self, **kwargs):
        context = super(InspirationUserView, self).get_context_data(**kwargs)
        context['examples'] = Example.objects.for_gallery_preview(challenge=context['challenge'])
        return context

    def get_user_role(self):
        return self.request.user.profile.role_name

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
            return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={
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

@login_required
@enforce_membership_challenge_access
def preview_stage(request, challenge_id, stage):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request,
        [
            'challenges/edp/preview/%s/%s.html' % (request.user.profile.user_type, stage),
            'challenges/edp/preview/%s.html' % stage,
        ],
        {
            'challenge': challenge,
            'comment_form': CommentForm(),
            'edp_nav': {
                'stage': stage,
                'inspiration': reverse("challenges:preview_inspiration", kwargs={"challenge_id": challenge.id}),
                'plan': reverse("challenges:preview_plan", kwargs={"challenge_id": challenge.id}),
                'build': reverse("challenges:preview_build", kwargs={"challenge_id": challenge.id}),
                'reflect': reverse("challenges:preview_reflect", kwargs={"challenge_id": challenge.id}),
            },
        }
    )

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

    progress.get_unread_comments_for_user(request.user).mark_all_as_read()

    quiz = challenge.quiz_set.exclude(is_active=False).exclude(result__user=request.user).first()
    quiz_form = None
    if quiz:
        quiz_form = QuizForm(model=quiz)

    return render(request,
        [
            "challenges/edp/progress/%s/%s.html" % (request.user.profile.user_type, stageToShow.name),
            "challenges/edp/progress/%s.html" % stageToShow.name,
        ],     
        {
        'challenge': challenge,
        'progress': progress,
        'comment_form': CommentForm(),
        'comments': progress.comments.all(),
        'materials_form': MaterialsForm(progress=progress),
        'quiz_form': quiz_form,
        'edp_nav': {
            'stage': stageToShow.name,
            'inspiration': reverse("challenges:inspiration_progress", kwargs={"challenge_id": challenge.id, "username": username}),
            'plan': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "plan"}),
            'build': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "build"}),
            'reflect': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "reflect"}),
        },
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
