from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import mentor_only
from curiositymachine.views.generic import UserJoinView
from django.http import HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.db.models import Count
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.models import Profile, UserRole
from profiles.forms.mentor import MentorUserAndProfileForm, MentorUserAndProfileChangeForm
from training.models import Module
from challenges.models import Progress
from django.db import transaction
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.utils.functional import lazy
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

join = transaction.atomic(UserJoinView.as_view(
    form_class = MentorUserAndProfileForm,
    prefix = 'mentor',
    logged_in_redirect = lazy(reverse, str)('profiles:home'),
    success_message = 'Thanks for your interest in joining the Curiosity Machine mentor community! You will receive an email shortly with more information on how to get started.',
    success_url = '/'
))

@login_required
def home(request):
    training_modules = Module.objects.filter(draft=False)
    accessible_modules = training_modules
    completed_modules = [module for module in training_modules if module.is_finished_by_mentor(request.user)]
    uncompleted_modules = [module for module in training_modules if not module.is_finished_by_mentor(request.user)]

    startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
    progresses = Progress.objects.filter(
        mentor=request.user, started__gt=startdate
    ).select_related(
        'challenge',
        'challenge__image',
        'challenge__video',
        'mentor',
        'student',
        'student__profile',
        'student__profile__image'
    ).order_by(
        '-started'
    )[:4]

    unclaimed_days = [(day, Progress.unclaimed(day[0])[0]) for day in Progress.unclaimed_days()]

    claimable_progresses = Progress.objects.filter(
        mentor__isnull=True
    ).exclude(
        comments=None
    )
    source_and_counts = claimable_progresses.values('student__profile__source').annotate(count=Count('student__profile__source'))
    partnerships = {
        obj["student__profile__source"]: {
            "source": obj['student__profile__source'],
            "unclaimed": obj['count'],
            "example_progress": claimable_progresses.filter(
                    student__profile__source=obj['student__profile__source']
                ).select_related(
                    "challenge__image"
                ).order_by(
                    "-started"
                ).first()
        } for obj in source_and_counts
    }
    non_partnerships = partnerships.get('', None)
    if non_partnerships:
        del partnerships['']
    partnerships = sorted(partnerships.values(), key=lambda o: o.get('source').lower())

    return render(request, "profiles/mentor/home.html", {
        'progresses': progresses,
        'unclaimed_days': unclaimed_days,
        'training_modules': training_modules,
        'accessible_modules': accessible_modules,
        'completed_modules': completed_modules,
        'uncompleted_modules': uncompleted_modules,
        'progresses_by_partnership': partnerships,
        'non_partnership': non_partnerships
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = MentorUserAndProfileChangeForm(data=request.POST, instance=request.user, prefix="mentor")
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = MentorUserAndProfileChangeForm(instance=request.user, prefix="mentor")

    return render(request, 'profiles/mentor/profile_edit.html', {'form': form,})

def list_all(request):
    '''
    List of current mentors
    '''
    page = request.GET.get('page')
    mentors = Profile.objects.filter(role=UserRole.mentor.value, approved=True).select_related('user').order_by('-user__date_joined')

    paginator = Paginator(mentors, settings.DEFAULT_PER_PAGE)
    try:
        mentors = paginator.page(page)
    except PageNotAnInteger:
        mentors = paginator.page(1)
    except EmptyPage:
        mentors = paginator.page(paginator.num_pages)

    return render(request, "profiles/mentor-community.html", {
        'mentors': mentors,
    })

def show_profile(request, username):
    '''
    Page for viewing a mentor's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, role=UserRole.mentor.value)

    return render(request, "profiles/mentor/profile.html", {'mentor': user, 'mentor_profile': profile,})

@login_required
@mentor_only
def unclaimed_progresses(request, **kwargs):
    progresses = []
    grouping = "none"
    page = request.GET.get('page')

    if set(['year', 'month', 'day']).issubset(set(kwargs.keys())):
        selected_date = date(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        progresses = Progress.objects.filter(
            mentor__isnull=True, started__year=selected_date.year, started__month=selected_date.month, started__day=selected_date.day
        ).exclude(
            comments=None
        ).order_by(
            '-started'
        ).select_related(
           'challenge', 'student', 'student__profile', 'student__profile__image', 'challenge__image'
        )
        grouping = selected_date
    elif "source" in request.GET:
        grouping = request.GET["source"]
        progresses = Progress.objects.filter(
                mentor__isnull=True, student__profile__source=grouping
        ).exclude(
                comments=None
        ).order_by(
                '-started'
        ).select_related(
                'challenge', 'student', 'student__profile', 'student__profile__image', 'challenge__image'
        )
        if grouping == "":
            grouping = "other"
    else:
        raise Http404()

    paginator = Paginator(progresses, settings.DEFAULT_PER_PAGE)
    try:
        progresses = paginator.page(page)
    except PageNotAnInteger:
        progresses = paginator.page(1)
    except EmptyPage:
        progresses = paginator.page(paginator.num_pages)

    return render(request, 'profiles/unclaimed_list.html', {
        'claimed': False,
        'grouping': grouping,
        'progresses': progresses
    })

@login_required
@mentor_only
def claimed_progresses(request, **kwargs):
    progresses = []
    page = request.GET.get('page')

    progresses = Progress.objects.filter(
        mentor=request.user
    ).order_by(
        '-started', 'id'
    ).select_related(
        'challenge', 'mentor', 'student', 'student__profile', 'student__profile__image', 'challenge__image'
    )

    paginator = Paginator(progresses, settings.DEFAULT_PER_PAGE)
    try:
        progresses = paginator.page(page)
    except PageNotAnInteger:
        progresses = paginator.page(1)
    except EmptyPage:
        progresses = paginator.page(paginator.num_pages)

    return render(request, 'profiles/claimed_list.html', {
        'claimed': True,
        'progresses': progresses
    })
