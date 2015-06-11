from django.shortcuts import render
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from profiles.forms import educator as forms
from curiositymachine.decorators import feature_flag, educator_only
from django.contrib.auth.decorators import login_required
from groups.forms import GroupForm
from units.models import Unit

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = forms.EducatorUserAndProfileForm(data=request.POST, prefix='educator')
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'profiles/educator/join.html', {
                'form': form
            })
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            form = forms.EducatorUserAndProfileForm(prefix='educator')
            return render(request, 'profiles/educator/join.html', {
                'form': form
            })

@login_required
@transaction.atomic
def profile_edit(request):
    if request.method == 'POST':
        form = forms.EducatorUserAndProfileForm(data=request.POST, instance=request.user, prefix='educator')
        if form.is_valid():
            form.save();
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = forms.EducatorUserAndProfileForm(instance=request.user, prefix='educator')

    return render(request, 'profiles/educator/profile_edit.html', {
        'form': form
    })

@educator_only
@login_required
def home(request):
    return render(request, "profiles/educator/home.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.all().order_by('id'),
    })
