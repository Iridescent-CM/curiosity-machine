from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.models import Profile
from profiles.forms import JoinForm, MentorProfileEditForm, StudentProfileEditForm
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
                return HttpResponseRedirect('/')
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        form = JoinForm()

    return render(request, 'join.html', {'form': form,})

@login_required
def home(request):
    if request.user.profile.is_mentor:
        progresses = Progress.objects.filter(mentor=request.user).select_related("challenge")
        unclaimed_progresses = Progress.objects.filter(mentor__isnull=True)
        challenges = {progress.challenge for progress in progresses}
        return render(request, "mentor_home.html", {'challenges':challenges, 'progresses': progresses,'unclaimed_progresses': unclaimed_progresses})
    else:
        filter = request.GET.get('filter')
        progresses = Progress.objects.filter(student=request.user).select_related("challenge")
        completed_progresses = [progress for progress in progresses if progress.completed]
        active_progresses = [progress for progress in progresses if not progress.completed]
        return render(request, "student_home.html", {'active_progresses': active_progresses, 'completed_progresses': completed_progresses, 'progresses': progresses, 'filter': filter})

def mentors(request):
    '''
    List of current mentors
    '''
    mentors = Profile.objects.filter(is_mentor=True)
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
