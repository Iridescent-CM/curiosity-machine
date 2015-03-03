from django.shortcuts import render
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.forms import JoinForm, StudentProfileEditForm
from profiles.forms.student import ConsentForm
from profiles.utils import create_or_edit_user
from challenges.models import Progress, Favorite
from django.db import transaction
from django.contrib import messages
from profiles.models import Profile, INVITATIONS_NS
from django_simple_redis import redis

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = JoinForm(request=request, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['is_student'] = True
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

@login_required
def home(request):
    filter = request.GET.get('filter')
    my_challenges_filters = [ 'active', 'completed', 'all' ]
    favorite_challenges = Favorite.objects.filter(student=request.user)
    progresses = Progress.objects.filter(student=request.user).select_related("challenge")
    completed_progresses = [progress for progress in progresses if progress.completed]
    active_progresses = [progress for progress in progresses if not progress.completed]
    return render(request, "student_home.html", {'active_progresses': active_progresses, 'completed_progresses': completed_progresses, 'progresses': progresses, 'filter': filter, 'my_challenges_filters': my_challenges_filters, 'favorite_challenges': favorite_challenges})

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

def signed_consent_form(request, profile_id):
    print(profile_id)
    profile = Profile.objects.get(pk=int(profile_id))
    return render(request, 'signed_consent_form.html', {'profile': profile})

def consent_form(request, token):
    #get the token from the invite email
    ctx = {
        'token': token
    }
    if request.method == 'POST':
        form = ConsentForm(data=request.POST)
        if form.is_valid():
            student = Profile.consent_student(token, form.cleaned_data['signature'])
            messages.success(request, 'Your consent form for Curiosity Machine was successfully signed and {username} account is now active!.'.format(username=student.user.username))
            return HttpResponseRedirect(reverse('profiles:home'))
    else:
        if redis.get(INVITATIONS_NS.format(token=token)):
            ctx['form'] = ConsentForm()
            return render(request, 'consent_form.html', ctx)
        else:
            messages.error(request, 'Consent form was not found')
            return HttpResponseRedirect(reverse('profiles:home'))

def resend_consent_form_email(request):
    request.user.profile.deliver_welcome_email()
    messages.success(request, 'Activation Consent form was resent')
    return HttpResponseRedirect(reverse('profiles:home'))
