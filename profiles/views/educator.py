from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Prefetch, Count
from ..forms import educator as forms
from ..decorators import membership_selection
from ..models import UserRole
from challenges.models import Challenge, Example
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
        students = membership.members.filter(profile__role=UserRole.student.value).select_related('profile')
    return render(request, "profiles/educator/dashboard/students.html", {
        "membership": membership,
        "students": students,
        "membership_selection": membership_selection,
    })

class Reversed:
    """
    Reverses the natural sort order of the value
    """

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return other.value < self.value

def latest_student_comment_sort(o):
    """
    Sorts by most recent latest_student_comment creation date first, then breaks ties with challenge name.
    Objects without a latest_student_comment come after objects with.
    """
    if o.latest_student_comment:
        return (0, Reversed(o.latest_student_comment.created), o.challenge.name)
    else:
        return (1, o.challenge.name)

@educator_only
@login_required
def student_detail(request, student_id):
    student = get_object_or_404(User.objects.select_related('profile'), pk=student_id)
    progresses = (student.progresses
        .select_related('challenge', 'mentor')
        .prefetch_related(
            'comments',
            Prefetch('example_set', queryset=Example.objects.status(approved=True), to_attr='approved_examples')
        )
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
        progress.student_comment_counts_by_stage = counts_by_stage[1:] # FIXME: you can't comment in the inspiration stage, but this way of doing it is opaque.

        progress.complete = counts_by_stage[4] != 0


    progresses = sorted(progresses, key=latest_student_comment_sort)

    return render(request, "profiles/educator/dashboard/student_detail.html", {
        "student": student,
        "progresses": progresses,
        "completed_count": len([p for p in progresses if p.complete])
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
