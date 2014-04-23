from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from profiles.models import Profile
from profiles.forms import JoinForm, ProfileEditForm
from profiles.utils import create_or_edit_user
from challenges.models import Challenge, Progress
from django.db import transaction

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = JoinForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                create_or_edit_user(request, data)
            except IntegrityError:
                errors = form._errors.setdefault('username', ErrorList())
                errors.append('Username has already been used')
            else:
                user = auth.authenticate(username=data['username'], password=data['password'])
                auth.login(request, user)
                return HttpResponseRedirect(request.user.profile.get_absolute_url())
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
        form = JoinForm()

    return render(request, 'join.html', {'form': form,})

@login_required
def home(request):
    if request.user.profile.is_mentor:
        progresses = Progress.objects.filter(mentor=request.user)
        challenges = []
        for progress in progresses:
            if not progress.challenge in challenges:
                challenges.append(progress.challenge)
        return render(request, "mentor_home.html", {'challenges':challenges, 'progresses': progresses,})
    else:
        progresses = Progress.objects.filter(student=request.user)
        return render(request, "student_home.html", {'progresses': progresses,})

def student_profile_details(request, username):
    '''
    Page for viewing a student's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=False)

    if user == request.user:
        template = 'user_profile.html'
    else:
        template = 'profile_details.html'

    return render(request, template, {'user': user, 'profile': profile,})

def mentor_profile_details(request, username):
    '''
    Page for viewing a mentor's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=True)

    if user == request.user:
        template = 'user_profile.html'
    else:
        template = 'profile_details.html'

    return render(request, template, {'user': user, 'profile': profile,})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request=request, data=request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            create_or_edit_user(request, data, request.user)
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
    else:
        form = ProfileEditForm(request)

    return render(request, 'profile_edit.html', {'form': form,})
