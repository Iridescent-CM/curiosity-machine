from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from profiles.models import Profile
from profiles.forms import JoinForm, ProfileEditForm
from profiles.utils import create_or_edit_user
from challenges.models import Challenge
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
    template_values = {
        'form': form,
    }

    return render(request, 'join.html', template_values)

def home(request):
    if request.user.profile.is_mentor:
        challenges = Challenge.objects.filter(mentor=request.user)
        return render(request, "mentor_home.html", {'challenges': challenges,})
    else:
        challenges = Challenge.objects.filter(students=request.user)
        return render(request, "student_home.html", {'challenges': challenges,})



def student_profile_details(request, username):
    '''
    Page for viewing a users profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=False)

    if user == request.user:
        template = 'user_profile.html'
    else:
        template = 'profile_details.html'

    template_values = {
        'user': user,
        'profile': profile,
    }

    return render(request, template, template_values)

def mentor_profile_details(request, username):
    '''
    Page for viewing a users profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=True)

    if user == request.user:
        template = 'user_profile.html'
    else:
        template = 'profile_details.html'

    template_values = {
        'user': user,
        'profile': profile,
    }

    return render(request, template, template_values)

def profile_edit(request):
    if not request.user.is_authenticated():
        raise Http404

    if request.method == 'POST':
        form = ProfileEditForm(request=request, data=request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            create_or_edit_user(request, data, request.user)
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
    else:
        form = ProfileEditForm(request)
    template_values = {
        'form': form,
    }

    return render(request, 'profile_edit.html', template_values)
