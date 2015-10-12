from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import mentor_only
from curiositymachine.views.generic import UserJoinView
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.models import Profile
from profiles.forms.mentor import MentorUserAndProfileForm, MentorUserAndProfileChangeForm
from training.models import Module
from challenges.models import Progress
from django.db import transaction
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.utils.functional import lazy
from django.conf import settings
import logging

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
    
    progresses = Progress.objects.filter(mentor=request.user, started__gt=startdate).order_by('-started').select_related("challenge")
    unclaimed_days = [(day, Progress.unclaimed(day[0])[0]) for day in Progress.unclaimed_days()]
    challenges = {progress.challenge for progress in progresses}
    return render(request, "mentor_home.html", {'challenges':challenges, 'progresses': progresses,'unclaimed_days': unclaimed_days, 'training_modules': training_modules, 'accessible_modules': accessible_modules, 'completed_modules': completed_modules, 'uncompleted_modules': uncompleted_modules})

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
    mentors = Profile.objects.filter(is_mentor=True, approved=True).order_by('-user__date_joined')
    return render(request, "profiles/mentor-community.html", {
        'mentors': mentors,
    })

def show_profile(request, username):
    '''
    Page for viewing a mentor's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=True)

    return render(request, "mentor_profile.html", {'user': user, 'profile': profile,})

@login_required
@mentor_only
def unclaimed_progresses(request, year, month, day):
    selected_date = date(int(year), int(month), int(day))
    progresses = Progress.unclaimed(selected_date)
    return render(request, 'mentor_unclaimed_challenges.html', {'date': selected_date, 'progresses': progresses})
