from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.models import Profile
from profiles.forms import JoinForm, MentorJoinForm, MentorProfileEditForm, StudentProfileEditForm
from profiles.utils import create_or_edit_user
from training.models import Module
from challenges.models import Challenge, Progress, Favorite
from django.db import transaction
import password_reset.views
import password_reset.forms

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = JoinForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                create_or_edit_user(data)
            except IntegrityError:
                errors = form._errors.setdefault('username', ErrorList())
                errors.append('Username has already been used')
                return render(request, 'join.html', {'form': form,})
            else:
                user = auth.authenticate(username=data['username'], password=data['password'])
                auth.login(request, user)
                user.profile.deliver_welcome_email()
                return HttpResponseRedirect('/')
        else:
            return render(request, 'join.html', {'form': form,})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        form = JoinForm()

    return render(request, 'join_modal.html', {'form': form,})

@transaction.atomic
def join_as_mentor(request):
    if request.method == 'POST':
        form = MentorJoinForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['is_mentor'] = True
            try:
                create_or_edit_user(data)
            except IntegrityError:
                errors = form._errors.setdefault('username', ErrorList())
                errors.append('Username has already been used')
                return render(request, 'join.html', {'form': form,})
            else:
                user = auth.authenticate(username=data['username'], password=data['password'])
                auth.login(request, user)
                user.profile.deliver_welcome_email()
                messages.success(request, 'Thanks for your interest in joining the Curiosity Machine mentor community! You will receive an email shortly with more information on how to get started.')
                return HttpResponseRedirect('/')
        else:
            return render(request, 'mentor_join.html', {'form': form,})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        form = MentorJoinForm()

    return render(request, 'mentor_join_modal.html', {'form': form,})

@login_required
def home(request):
    if request.user.profile.is_mentor:
        training_modules = Module.objects.all()
        accessible_modules = training_modules
        completed_modules = [module for module in training_modules if module.is_finished_by_mentor(request.user)]
        uncompleted_modules = [module for module in training_modules if not module.is_finished_by_mentor(request.user)]
        progresses = Progress.objects.filter(mentor=request.user).order_by('-started').select_related("challenge")
        unclaimed_progresses = Progress.unclaimed()
        challenges = {progress.challenge for progress in progresses}
        return render(request, "mentor_home.html", {'challenges':challenges, 'progresses': progresses,'unclaimed_progresses': unclaimed_progresses, 'training_modules': training_modules, 'accessible_modules': accessible_modules, 'completed_modules': completed_modules, 'uncompleted_modules': uncompleted_modules})
    else:
        filter = request.GET.get('filter')
        my_challenges_filters = [ 'active', 'completed', 'all' ]
        favorite_challenges = Favorite.objects.filter(student=request.user)
        progresses = Progress.objects.filter(student=request.user).select_related("challenge")
        completed_progresses = [progress for progress in progresses if progress.completed]
        active_progresses = [progress for progress in progresses if not progress.completed]
        return render(request, "student_home.html", {'active_progresses': active_progresses, 'completed_progresses': completed_progresses, 'progresses': progresses, 'filter': filter, 'my_challenges_filters': my_challenges_filters, 'favorite_challenges': favorite_challenges})

def mentors(request):
    '''
    List of current mentors
    '''
    mentors = Profile.objects.filter(is_mentor=True, approved=True)
    return render(request, "mentors.html", {'mentors': mentors,})

def mentor_profile(request, username):
    '''
    Page for viewing a mentor's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=True)

    return render(request, "mentor_profile.html", {'user': user, 'profile': profile,})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        if request.user.profile.is_mentor:
            form = MentorProfileEditForm(request=request, data=request.POST)
        else:
            form = StudentProfileEditForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_or_edit_user(data, request.user)
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        if request.user.profile.is_mentor:
            form = MentorProfileEditForm(request)
        else:
            form = StudentProfileEditForm(request)

    return render(request, 'profile_edit.html', {'form': form,})

def underage_student(request):
    return render(request, 'underage_student.html')

### password recovery

class Recover(password_reset.views.Recover):
    search_fields = ['username'] # search only on username, not on email. this is important because email is not a unique field in this app!

recover = Recover.as_view()
