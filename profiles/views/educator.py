from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Prefetch, Count
from collections import OrderedDict
from ..forms import educator as forms
from ..decorators import membership_selection
from ..models import UserRole
from ..sorting import latest_student_comment_sort, StudentSorter
from challenges.models import Challenge, Example, Stage
from cmcomments.models import Comment
from units.models import Unit
from memberships.models import Member
from curiositymachine.decorators import educator_only
from curiositymachine.views.generic import UserJoinView
from django.utils.functional import lazy

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
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        sorter = StudentSorter(query=request.GET)
        students = membership.members.filter(profile__role=UserRole.student.value).select_related('profile')
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
    student = get_object_or_404(User.objects.select_related('profile'), pk=student_id)
    membership = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
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
            student_comments = [c for c in progress.comments.all() if c.user_id == student.id]
            progress.total_student_comments = len(student_comments)

            if student_comments:
                progress.latest_student_comment = max(student_comments, key=lambda o: o.created)
            else:
                progress.latest_student_comment = None

            counts_by_stage = [0, 0, 0, 0, 0];
            for comment in student_comments:
                counts_by_stage[comment.stage] = counts_by_stage[comment.stage] + 1
            progress.student_comment_counts_by_stage = counts_by_stage[1:] # inspiration stage can't have comments

            progress.complete = counts_by_stage[Stage.reflect.value] != 0


        progresses = sorted(progresses, key=latest_student_comment_sort)

        return render(request, "profiles/educator/dashboard/student_detail.html", {
            "student": student,
            "progresses": progresses,
            "completed_count": len([p for p in progresses if p.complete]),
            "membership_selection": membership_selection,
        })

@educator_only
@login_required
@membership_selection
def guides_dashboard(request, membership_selection=None):
    units = Unit.objects.filter(listed=True).select_related('image')

    extra_units = []
    membership = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        extra_units = membership.extra_units.order_by('id').select_related('image')

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

    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        challenge = get_object_or_404(membership.challenges, pk=challenge_id) # FIXME: what if we're outside a membership?

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

        totals = OrderedDict(
            (
                student,
                OrderedDict.fromkeys([
                    Stage.plan.name,
                    Stage.build.name,
                    Stage.test.name,
                    Stage.reflect.name,
                ], 0)
            ) 
            for student in students
        )
        for comment in comments:
            stagename = Stage(comment.stage).name
            totals[comment.user][stagename] = totals[comment.user].get(stagename) + 1

        return render(request, "profiles/educator/dashboard/dc_detail.html", {
            "challenge": challenge,
            "challenge_links": membership.challenges.order_by('name').all(),
            "totals": totals,
            "student_ids_with_examples": student_ids_with_examples,
            "membership_selection": membership_selection,
            "sorter": sorter,
        })
