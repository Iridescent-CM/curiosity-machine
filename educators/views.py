from allauth.account.forms import SetPasswordForm
from challenges.models import Challenge, Example
from cmcomments.models import Comment
from curiositymachine import signals
from curiositymachine.decorators import whitelist
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, FormView, TemplateView, UpdateView, View
from memberships.helpers.selectors import GroupSelector
from profiles.decorators import only_for_role
from profiles.views import UserKwargMixin
from rest_framework import generics, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from units.models import Unit
from .annotators import *
from .decorators import *
from .forms import *
from .models import *
from .serializers import *
from .sorting import *

class CreateView(UserKwargMixin, CreateView):
    model = EducatorProfile
    form_class = EducatorProfileForm
    success_url = lazy(reverse, str)("educators:home")

create = CreateView.as_view()

class EditView(UserKwargMixin, UpdateView):
    model = EducatorProfile
    form_class = EducatorProfileForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("educators:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.educatorprofile

edit = EditView.as_view()

class ChallengesView(TemplateView):
    template_name = "educators/dashboard/challenges.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

        membership_challenges = []
        membership = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            gs = GroupSelector(membership)
            membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')
            core_challenges = core_challenges.exclude(id__in=membership_challenges.values('id'))

        context.update({
            "membership": membership,
            "membership_challenges": membership_challenges,
            "core_challenges": core_challenges,
            "membership_selection": membership_selection,
            "group_selector": gs,
        })

        return context

challenges = ChallengesView.as_view()

class ChallengeView(TemplateView):
    template_name = "educators/dashboard/challenge.html"

    def get_context_data(self, **kwargs):
        membership_selection = MembershipSelection(self.request)
        if not membership_selection.selected:
            raise PermissionDenied

        membership = membership_selection.selected
        challenge = get_object_or_404(membership.challenges, pk=self.kwargs.get('challenge_id'))

        sorter = StudentSorter(query=self.request.GET)
        gs = GroupSelector(membership, query=self.request.GET)
        students = gs.selected.queryset.select_related('profile__image')
        students = sorter.sort(students)
        students = students.select_related('profile__image').all()

        comments = (Comment.objects
            .filter(
                user__in=students,
                challenge_progress__challenge_id=challenge.id)
            .select_related('user', 'user__profile'))
        student_ids_with_examples = (Example.objects
            .filter(
                approved=True,
                progress__challenge_id=challenge.id,
                progress__student__in=students)
            .values_list('progress__student__id', flat=True))

        for student in students:
            UserCommentSummary(comments, student.id).annotate(student)

        kwargs.update({
            "challenge": challenge,
            "challenge_links": membership.challenges.order_by('name').all(),
            "students": students,
            "student_ids_with_examples": student_ids_with_examples,
            "membership_selection": membership_selection,
            "sorter": sorter,
            "group_selector": gs,
        })
        return super().get_context_data(**kwargs)

challenge = ChallengeView.as_view()

class StudentsView(TemplateView):
    template_name = "educators/dashboard/students.html"

    def get_context_data(self, **kwargs):
        request = self.request
        membership = None
        students = []
        sorter = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            sorter = StudentSorter(query=request.GET)
            gs = GroupSelector(membership, query=request.GET)
            students = gs.selected.queryset.select_related('profile__image')
            students = sorter.sort(students)

        kwargs.update({
            "membership": membership,
            "students": students,
            "group_selector": gs,
            "membership_selection": membership_selection,
            "sorter": sorter,
        })
        return super().get_context_data(**kwargs)

# TODO: make all role views role-only
students = StudentsView.as_view()

class StudentView(TemplateView):
    template_name = "educators/dashboard/student.html"

    def get_context_data(self, **kwargs):
        membership_selection = MembershipSelection(self.request)
        if not membership_selection.selected:
            raise PermissionDenied

        membership = membership_selection.selected
        membership_students = membership.members.select_related('profile__image').filter(extra__role=UserRole.student.value)
        student = get_object_or_404(membership_students, pk=self.kwargs.get('student_id'))
        progresses = (student.progresses
            .filter(comments__isnull=False, challenge__in=membership.challenges.all())
            .select_related('challenge', 'mentor')
            .prefetch_related(
                'comments',
                Prefetch('example_set', queryset=Example.objects.status(approved=True), to_attr='approved_examples')
            )
            .distinct()
            .all())

        for progress in progresses:
            UserCommentSummary(progress.comments.all(), student.id).annotate(progress)
        sorter = ProgressSorter(query=self.request.GET)
        progresses = sorter.sort(progresses)

        graph_data_url = "%s?%s" % (reverse('educators:progress_graph_data'), "&".join(["id=%d" % p.id for p in progresses]))

        kwargs.update({
            "student": student,
            "progresses": progresses,
            "completed_count": len([p for p in progresses if p.complete]),
            "membership_selection": membership_selection,
            "sorter": sorter,
            "graph_data_url": graph_data_url,
        })
        return super().get_context_data(**kwargs)

student = StudentView.as_view()

class StudentPasswordResetView(FormView):
    template_name = "educators/dashboard/password_reset.html"
    form_class = SetPasswordForm
    success_url = lazy(reverse, str)("educators:students")

    def dispatch(self, request, *args, **kwargs):
        self.membership_selection = MembershipSelection(request)
        membership = self.membership_selection.selected
        membership_students = (membership.members
            .select_related('profile__image')
            .filter(extra__role=UserRole.student.value))
        self.student = get_object_or_404(membership_students, pk=self.kwargs.get('student_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.student
        })
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.update({
            "student": self.student,
            "membership_selection": self.membership_selection
        })
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.save()
        signals.student_password_changed.send(
            sender=self.student,
            student=self.student,
            resetter=self.request.user
        )
        messages.success(self.request, "%s's password successfully changed." % self.student.username)
        return super().form_valid(form)

student_password_reset = StudentPasswordResetView.as_view()

class GuidesView(TemplateView):
    template_name = "educators/dashboard/guides.html"

    def get_context_data(self, **kwargs):
        units = Unit.objects.filter(listed=True).order_by('id').select_related('image')

        extra_units = []
        membership = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            extra_units = membership.extra_units.order_by('id').select_related('image')
            units = units.exclude(id__in=extra_units.values('id'))

        kwargs.update({
            "units": units,
            "membership": membership,
            "extra_units": extra_units,
            "membership_selection": membership_selection,
        })

        return super().get_context_data(**kwargs)

# TODO: make impact survey and membership selection part of a dashboard mixin?
guides = GuidesView.as_view()

class ImpactSurveySubmitView(View):
    http_method_names=['post']

    def post(self, request, *args, **kwargs):
        survey = ImpactSurvey.objects.create(user=request.user)
        form = ImpactSurveyForm(data=request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({
                "status": "invalid",
                "errors": form.errors
            }, status=400)

impact_data = whitelist('public')(
    only_for_role('educator')(
        ImpactSurveySubmitView.as_view()))

class IsEducator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.extra.is_educator

class CommentList(generics.ListAPIView):
    renderer_classes = (JSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsEducator)

    def get_queryset(self):
        queryset = Comment.objects.none()
        ids = self.request.query_params.getlist('id', None)
        if ids is not None:
            queryset = (Comment.objects
                .filter(challenge_progress__student__membership__members=self.request.user)
                .filter(challenge_progress_id__in=ids)
                .select_related('user__profile', 'challenge_progress')
                .all()
            )
        return queryset

comments = whitelist('public')(CommentList.as_view())
