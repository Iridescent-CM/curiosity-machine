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
        progresses = Progress.objects.filter(mentor=request.user).select_related("challenge")
        challenges = {progress.challenge for progress in progresses}
        return render(request, "mentor_home.html", {'challenges':challenges, 'progresses': progresses,})
    else:
        progresses = Progress.objects.filter(student=request.user).select_related("challenge")
        return render(request, "student_home.html", {'progresses': progresses,})

def profile_details(request, username, mentor=False):
    '''
    Page for viewing a student or mentor's profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=mentor)

    return render(request, "profile_details.html", {'user': user, 'profile': profile,})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request=request, data=request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            create_or_edit_user(data, request.user)
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
    else:
        form = ProfileEditForm(request)

    return render(request, 'profile_edit.html', {'form': form,})


### password recovery

class Recover(password_reset.views.Recover):
    search_fields = ['username'] # search only on username, not on email. this is important because email is not a unique field in this app!

recover = Recover.as_view()
