from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Count
from django.conf import settings
from collections import OrderedDict
from ..forms import educator as forms
from ..forms import ImpactSurveyForm
from ..decorators import membership_selection, impact_survey
from ..models import UserRole, ImpactSurvey
from ..sorting import StudentSorter, ProgressSorter
from ..annotators import UserCommentSummary
from challenges.models import Challenge, Example, Stage
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from units.models import Unit
from memberships.models import Member
from curiositymachine.decorators import educator_only, feature_flag
from curiositymachine.views.generic import UserJoinView
from curiositymachine import signals
from django.utils.functional import lazy
from rest_framework import generics, permissions
from ..serializers import CommentSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from memberships.helpers.selectors import GroupSelector
from django.template.response import TemplateResponse

User = get_user_model()

join = transaction.atomic(UserJoinView.as_view(
    form_class = forms.EducatorUserAndProfileForm,
    prefix = 'educator',
    logged_in_redirect = lazy(reverse, str)('profiles:home'),
    success_url = '/'
))

@login_required
@transaction.atomic
def profile_edit(request):
    if request.method == 'POST':
        form = forms.EducatorUserAndProfileForm(data=request.POST, instance=request.user, prefix='educator')
        if form.is_valid():
            form.save();
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = forms.EducatorUserAndProfileForm(instance=request.user, prefix='educator')

    return render(request, 'profiles/educator/profile_edit.html', {
        'form': form
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def password_reset(request, student_id, membership_selection=None):
    membership = membership_selection.selected
    membership_students = membership.members.select_related('profile__image').filter(profile__role=UserRole.student.value)
    student = get_object_or_404(membership_students, pk=student_id)

    if request.method == 'POST':
        form = SetPasswordForm(student, data=request.POST)
        if form.is_valid():
            form.save()
            signals.student_password_changed.send(sender=student, student=student, resetter=request.user)
            messages.success(request, "%s's password successfully changed." % student.username)
            return redirect('profiles:educator_dashboard_students')
    else:
        form = SetPasswordForm(student)

    return TemplateResponse(request, 'profiles/educator/dashboard/student_password.html', {
        'student': student,
        "membership_selection": membership_selection,
        'form': form
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def home(request, membership_selection=None):
    core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

    membership_challenges = []
    membership = None
    gs = None
    if membership_selection and membership_selection.selected:
        membership = membership_selection.selected
        gs = GroupSelector(membership)
        membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')
        core_challenges = core_challenges.exclude(id__in=membership_challenges.values('id'))

    return TemplateResponse(request, "profiles/educator/dashboard/challenges.html", {
        "membership": membership,
        "membership_challenges": membership_challenges,
        "core_challenges": core_challenges,
        "membership_selection": membership_selection,
        "group_selector": gs,
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def students_dashboard(request, membership_selection=None):
    membership = None
    students = []
    sorter = None
    gs = None
    if membership_selection and membership_selection.selected:
        membership = membership_selection.selected
        sorter = StudentSorter(query=request.GET)
        gs = GroupSelector(membership, query=request.GET)
        students = gs.selected.queryset.select_related('profile__image')
        students = sorter.sort(students)
    return TemplateResponse(request, "profiles/educator/dashboard/students.html", {
        "membership": membership,
        "students": students,
        "group_selector": gs,
        "membership_selection": membership_selection,
        "sorter": sorter,
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def student_detail(request, student_id, membership_selection=None):
    if not (membership_selection and membership_selection.selected):
        raise PermissionDenied

    membership = membership_selection.selected
    membership_students = membership.members.select_related('profile__image').filter(profile__role=UserRole.student.value)
    student = get_object_or_404(membership_students, pk=student_id)
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
    sorter = ProgressSorter(query=request.GET)
    progresses = sorter.sort(progresses)

    graph_data_url = "%s?%s" % (reverse('profiles:progress_graph_data'), "&".join(["id=%d" % p.id for p in progresses]))

    return TemplateResponse(request, "profiles/educator/dashboard/student_detail.html", {
        "student": student,
        "progresses": progresses,
        "completed_count": len([p for p in progresses if p.complete]),
        "membership_selection": membership_selection,
        "sorter": sorter,
        "graph_data_url": graph_data_url,
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def guides_dashboard(request, membership_selection=None):
    units = Unit.objects.filter(listed=True).order_by('id').select_related('image')

    extra_units = []
    membership = None
    if membership_selection and membership_selection.selected:
        membership = membership_selection.selected
        extra_units = membership.extra_units.order_by('id').select_related('image')
        units = units.exclude(id__in=extra_units.values('id'))

    return TemplateResponse(request, "profiles/educator/dashboard/guides.html", {
        "units": units,
        "membership": membership,
        "extra_units": extra_units,
        "membership_selection": membership_selection,
    })

@educator_only
@login_required
@membership_selection
@impact_survey
def challenge_detail(request, challenge_id, membership_selection=None):
    if not (membership_selection and membership_selection.selected):
        raise PermissionDenied

    membership = membership_selection.selected
    challenge = get_object_or_404(membership.challenges, pk=challenge_id)

    sorter = StudentSorter(query=request.GET)
    gs = GroupSelector(membership, query=request.GET)
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

    return TemplateResponse(request, "profiles/educator/dashboard/dc_detail.html", {
        "challenge": challenge,
        "challenge_links": membership.challenges.order_by('name').all(),
        "students": students,
        "student_ids_with_examples": student_ids_with_examples,
        "membership_selection": membership_selection,
        "sorter": sorter,
        "group_selector": gs,
    })

class IsEducator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.is_educator

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

@educator_only
@login_required
@membership_selection
@impact_survey
@feature_flag('enable_educator_feedback')
def conversation(request, student_id, challenge_id, membership_selection=None):
    if not (membership_selection and membership_selection.selected):
        raise PermissionDenied

    membership = membership_selection.selected
    student = get_object_or_404(membership.members, pk=student_id)
    progress = get_object_or_404(student.progresses, challenge_id=challenge_id)
    return TemplateResponse(request, "profiles/educator/dashboard/conversation.html", {
        "membership_selection": membership_selection,
        "student": student,
        "progress": progress,
        "comments": progress.comments.order_by("-created").all(),
        "comment_form": CommentForm(),
    })

from django.views.generic import View
from django.http import JsonResponse, HttpResponse
import time

class ImpactSurveyView(View):
    http_method_names=['post']

    def post(self, request, *args, **kwargs):
        survey = ImpactSurvey.objects.get_or_create(user=request.user)[0]
        form = ImpactSurveyForm(data=request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({
                "status": "invalid",
                "errors": form.errors
            }, status=400)
