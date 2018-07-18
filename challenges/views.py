from cmcomments.forms import CommentForm
from curiositymachine.decorators import current_user_or_approved_viewer, mentor_only
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic.base import View, TemplateView
from feedback.forms import FeedbackQuestionForm
from images.models import Image
from memberships.decorators import enforce_membership_challenge_access
from memberships.models import Membership
from profiles.decorators import only_for_role
from profiles.models import UserRole
from quizzes.forms import QuizForm
from .filtersets import *
from .forms import MaterialsForm
from .models import *
from .utils import get_stage_for_progress

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

class ChallengesListView(View):
    template_name = "challenges/list.html"
    filterset_classes = [
        UnfilteredChallenges,
        MembershipChallenges,
        AIFCChallenges,
        FilterChallenges,
        ThemeChallenges,
    ]

    def get(self, request, *args, **kwargs):
        filtersets = [ cls(self.request) for cls in self.filterset_classes ]
        active_filterset = next((f for f in filtersets if f.requested), filtersets[0])

        template_name, context, response = active_filterset.apply()
        if response:
            return response

        if 'challenges' in context:
            context['challenges'] = context['challenges'].filter(draft=False).select_related('image')

            if self.request.user.is_authenticated() and not self.request.user.extra.is_student:
                context['challenges'] = context['challenges'].annotate(has_resources=Count('resource'))

            context['challenges'] = _paginate(context['challenges'], self.request.GET.get('page'), settings.CHALLENGES_PER_PAGE)

            if self.request.user.is_authenticated():
                _decorate_started(self.request, context['challenges'])

            context['challenges'] = _decorate_access(self.request, context['challenges'])

        favorite_ids = set()
        if self.request.user.is_authenticated():
            favorite_ids = set(Favorite.objects.filter(student=self.request.user).values_list('challenge__id', flat=True))

        context['filters'] = []
        for filterset in filtersets:
            context['filters'] += filterset.get_template_contexts()

        return TemplateResponse(
            request=request,
            template=template_name or self.template_name,
            context=context
        )

challenges = ChallengesListView.as_view()

@require_POST
@only_for_role(UserRole.student, UserRole.family)
@enforce_membership_challenge_access
def start_building(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    try:
        Progress.objects.get_or_create(challenge=challenge, owner=request.user)
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
        return self.request.user.extra.role_name

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
            owner__username = kwargs.get('username')
        )
        return context

class InspirationStudentPreview(InspirationUserPreview):

    def get(self, request, *args, **kwargs):
        username = self.request.user.username
        challenge_id = kwargs.get('challenge_id')
        if Progress.objects.filter(
            challenge=challenge_id,
            owner__username=username
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
            if user.extra.is_student:
                return InspirationStudentPreview
            else:
                return InspirationUserPreview
        else:
            return InspirationAnonymousPreview

class InspirationProgressDispatch(ViewDispatch):

    @staticmethod
    def select_view_class(user):
        if user.is_authenticated():
            if user.extra.is_student:
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
            'challenges/edp/preview/%s/%s.html' % (request.user.extra.user_type, stage),
            'challenges/edp/preview/%s/%s.html' % (request.user.extra.role_name, stage),
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
        progress = Progress.objects.get(challenge=challenge, owner__username=username)
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
        progress = Progress.objects.get(challenge=challenge, owner__username=username)
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

    feedback_question = challenge.feedback_question
    feedback_form = None
    feedback_question_text = None
    feedback_response_text = None

    if feedback_question and feedback_question.is_active:
        feedback_form = FeedbackQuestionForm(model=feedback_question)
        feedback_question_text = feedback_question.question

    feedback_response = challenge.feedbackresult_set.filter(user=request.user).first()
    if feedback_response:
        feedback_response_text = feedback_response.answer

    return render(request,
        [
            "challenges/edp/progress/%s/%s.html" % (request.user.extra.user_type, stageToShow.name),
            "challenges/edp/progress/%s/%s.html" % (request.user.extra.role_name, stageToShow.name),
            "challenges/edp/progress/%s.html" % stageToShow.name,
        ],
        {
        'challenge': challenge,
        'progress': progress,
        'comment_form': CommentForm(),
        'comments': progress.comments.all(),
        'materials_form': MaterialsForm(progress=progress),
        'quiz_form': quiz_form,
        'feedback_form': feedback_form,
        'feedback_question': feedback_question_text,
        'feedback_response': feedback_response_text,
        'edp_nav': {
            'stage': stageToShow.name,
            'inspiration': reverse("challenges:inspiration_progress", kwargs={"challenge_id": challenge.id, "username": username}),
            'plan': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "plan"}),
            'build': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "build"}),
            'reflect': reverse("challenges:challenge_progress", kwargs={"challenge_id": challenge.id, "username": username, "stage": "reflect"}),
        },
    })

# Any POST to this assigns the current user to a progress as a mentor
# currently there is no security to stop a mentor from claiming a progress already claimed by another mentor by manually POSTing
@require_http_methods(["POST"])
@mentor_only
def claim_progress(request, progress_id):
    progress = get_object_or_404(Progress, id=progress_id)

    progress.mentor = request.user
    progress.save(update_fields=["mentor"])

    messages.success(request, 'You have successfully claimed this challenge.')

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': progress.challenge.id, 'username': progress.owner.username,}))
    #return HttpResponse(status=204)

# Any POST to this changes the materials list for that progress
@require_http_methods(["POST"])
def change_materials(request, challenge_id, username):
    progress = get_object_or_404(Progress, challenge_id=challenge_id, owner__username=username)

    form = MaterialsForm(request.POST, progress=progress)
    if form.is_valid():
        progress._materials_list = form.cleaned_data['materials']
        progress.save(update_fields=["_materials_list"])

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': progress.challenge.id, 'username': progress.owner.username, 'stage': 'plan'}))

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
            progress = Progress.objects.filter(challenge_id=challenge_id, owner=request.user).first()
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
        progress = Progress.objects.filter(challenge_id=challenge_id, owner=request.user).first()
        image = get_object_or_404(Image, id=request.POST.get('example'))

        if not image.comments.filter(user=request.user, challenge_progress=progress).exists():
            raise Http404("Image not found for this challenge")
        if Example.objects.from_progress(progress=progress).status(approved=True, pending=True).exists():
            return HttpResponse(status=409, reason="Example already exists")
        example = Example(progress=progress, image=image)
        example.save()
        return HttpResponseRedirect(reverse('challenges:examples', kwargs={
            'challenge_id': challenge.id,
        }))

class ExamplesDeleteView(View):
    @method_decorator(login_required)
    def post(self, request, challenge_id=None, *args, **kwargs):
        example = get_object_or_404(Example, id=request.POST.get('example-id'))
        if example.progress.owner != request.user:
            raise Http404()
        example.approved=False
        example.save()
        return HttpResponseRedirect(reverse('challenges:examples', kwargs={
            'challenge_id': challenge_id,
        }))
