from django.shortcuts import render
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.forms import StudentProfileEditForm
from profiles.forms.student import StudentUserAndProfileForm
from profiles.utils import create_or_edit_user
from groups.forms import GroupJoinForm, GroupLeaveForm
from groups.models import Invitation
from challenges.models import Progress, Favorite
from django.db import transaction

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = StudentUserAndProfileForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'join.html', {'form': form,})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        form = StudentUserAndProfileForm()

    return render(request, 'join.html', {'form': form,})

@login_required
def home(request):
    filter = request.GET.get('filter')
    my_challenges_filters = [ 'active', 'completed', 'all' ]
    favorite_challenges = Favorite.objects.filter(student=request.user)
    progresses = Progress.objects.filter(student=request.user).select_related("challenge")
    completed_progresses = [progress for progress in progresses if progress.completed]
    active_progresses = [progress for progress in progresses if not progress.completed]
    return render(request, "student_home.html", {
        'active_progresses': active_progresses, 
        'completed_progresses': completed_progresses, 
        'progresses': progresses, 
        'filter': filter, 
        'my_challenges_filters': my_challenges_filters, 
        'favorite_challenges': favorite_challenges,
        'group_form': GroupJoinForm(),
        'groups': request.user.cm_groups.all(),
        'invitations': Invitation.objects.filter(user=request.user).all()
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = StudentProfileEditForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_or_edit_user(data, request.user)
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = StudentProfileEditForm(request)

    return render(request, 'profile_edit.html', {'form': form,})

def underage(request):
    return render(request, 'underage_student.html')
