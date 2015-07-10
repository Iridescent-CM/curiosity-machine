from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import mentor_only
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
from django.conf import settings

@transaction.atomic
def join(request):
    templates = ["profiles/mentor/join.html"]
    if request.method == 'POST':
        form = MentorUserAndProfileForm(data=request.POST, prefix="mentor")
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            messages.success(request, 'Thanks for your interest in joining the Curiosity Machine mentor community! You will receive an email shortly with more information on how to get started.')
            return HttpResponseRedirect('/')
        else:
            return render(request, templates, {'form': form,})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            form = MentorUserAndProfileForm(prefix="mentor")
            return render(request, templates, {'form': form,})

@transaction.atomic
def join_from_source(request, source):

    templates = ["profiles/mentor/source/{}/join.html".format(source), "profiles/mentor/source/join.html"]
    initial = {
        'source': source
    }

    if request.method == 'POST':
        form = MentorUserAndProfileForm(data=request.POST, prefix="mentor")
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            messages.success(request, 'Thanks for your interest in joining the Curiosity Machine mentor community! You will receive an email shortly with more information on how to get started.')
            return HttpResponseRedirect('/')
        else:
            return render(request, templates, {'form': form, 'source': source})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            form = MentorUserAndProfileForm(prefix="mentor", initial=initial)
            return render(request, templates, {'form': form, 'source': source})

@login_required
def home(request):
    training_modules = Module.objects.all()
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
    mentors = Profile.objects.filter(is_mentor=True, approved=True)
    return render(request, "mentors.html", {'mentors': mentors,})

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
