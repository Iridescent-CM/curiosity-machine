from django.shortcuts import render
from django.contrib import auth, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import feature_flag
from django.core.urlresolvers import reverse
from profiles.forms import parent as forms

@transaction.atomic
@feature_flag('enable_parents')
def join(request):
    if request.method == 'POST':
        form = forms.ParentUserAndProfileForm(data=request.POST, prefix="parent")
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'profiles/parent/join.html', {
                'form': form
            })
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            form = forms.ParentUserAndProfileForm(prefix="parent")
            return render(request, 'profiles/parent/join.html', {
                'form': form
            })

@login_required
@feature_flag('enable_parents')
def home(request):
    return render(request, "profiles/parent/home.html", {})

@login_required
@transaction.atomic
@feature_flag('enable_parents')
def profile_edit(request):
    if request.method == 'POST':
        form = forms.ParentUserAndProfileForm(data=request.POST, instance=request.user, prefix="parent")
        if form.is_valid():
            form.save();
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = forms.ParentUserAndProfileForm(instance=request.user, prefix="parent")

    return render(request, 'profiles/parent/profile_edit.html', {
        'form': form
    })
