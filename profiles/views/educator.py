from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Count
from collections import OrderedDict
from ..forms import educator as forms
from ..decorators import membership_selection
from ..models import UserRole
from ..sorting import StudentSorter, ProgressSorter
from ..annotators import UserCommentSummary
from challenges.models import Challenge, Example, Stage
from cmcomments.models import Comment
from units.models import Unit
from memberships.models import Member
from curiositymachine.decorators import educator_only
from curiositymachine.views.generic import UserJoinView
from django.utils.functional import lazy
from rest_framework import generics, permissions
from ..serializers import CommentSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

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
def home(request, membership_selection=None):
    core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

    membership_challenges = []
    membership = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')
        core_challenges = core_challenges.exclude(id__in=membership_challenges.values('id'))

    return render(request, "profiles/educator/dashboard/challenges.html", {
        "membership": membership,
        "membership_challenges": membership_challenges,
        "core_challenges": core_challenges,
        "membership_selection": membership_selection,
    })

@educator_only
@login_required
@membership_selection
def students_dashboard(request, membership_selection=None):
    membership = None
    students = []
    sorter = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        sorter = StudentSorter(query=request.GET)
        students = membership.members.filter(profile__role=UserRole.student.value).select_related('profile__image')
        students = sorter.sort(students)
    return render(request, "profiles/educator/dashboard/students.html", {
        "membership": membership,
        "students": students,
        "membership_selection": membership_selection,
        "sorter": sorter,
    })

@educator_only
@login_required
@membership_selection
def student_detail(request, student_id, membership_selection=None):
    if not (membership_selection and membership_selection["selected"]):
        raise PermissionDenied

    membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
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

    return render(request, "profiles/educator/dashboard/student_detail.html", {
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
def guides_dashboard(request, membership_selection=None):
    units = Unit.objects.filter(listed=True).order_by('id').select_related('image')

    extra_units = []
    membership = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        extra_units = membership.extra_units.order_by('id').select_related('image')
        units = units.exclude(id__in=extra_units.values('id'))

    return render(request, "profiles/educator/dashboard/guides.html", {
        "units": units,
        "membership": membership,
        "extra_units": extra_units,
        "membership_selection": membership_selection,
    })

@educator_only
@login_required
@membership_selection
def challenge_detail(request, challenge_id, membership_selection=None):
    if not (membership_selection and membership_selection["selected"]):
        raise PermissionDenied

    membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
    challenge = get_object_or_404(membership.challenges, pk=challenge_id)

    sorter = StudentSorter(query=request.GET)
    students = membership.members.filter(profile__role=UserRole.student.value)
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

    return render(request, "profiles/educator/dashboard/dc_detail.html", {
        "challenge": challenge,
        "challenge_links": membership.challenges.order_by('name').all(),
        "students": students,
        "student_ids_with_examples": student_ids_with_examples,
        "membership_selection": membership_selection,
        "sorter": sorter,
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
