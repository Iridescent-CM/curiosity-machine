from django.shortcuts import render
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from profiles.forms import educator as forms
from curiositymachine.decorators import feature_flag, educator_only
from curiositymachine.views.generic import UserJoinView
from django.contrib.auth.decorators import login_required
from django.utils.functional import lazy
from groups.forms import GroupForm
from units.models import Unit

join = transaction.atomic(UserJoinView.as_view(
    form_class = forms.EducatorUserAndProfileForm,
    prefix = 'educator',
    logged_in_redirect = lazy(reverse, str)('profiles:home'),
    success_url = '/'
))

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
        'units': Unit.objects.filter(listed=True).order_by('id'),
        'memberships': request.user.membership_set.all()
    })

@educator_only
@login_required
def home_students(request):
    return render(request, "profiles/educator/home-students.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.filter(draft=False).order_by('id'),
        'memberships': request.user.membership_set.all()
    })

@educator_only
@login_required
def home_units(request):
    return render(request, "profiles/educator/home-units.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.filter(draft=False).order_by('id'),
        'memberships': request.user.membership_set.all()
    })

@educator_only
@login_required
def studentprogress(request):
    return render(request, "profiles/educator/student-progress.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.filter(draft=False).order_by('id'),
        'memberships': request.user.membership_set.all()
    })

@educator_only
@login_required
def dcprogress(request):
    return render(request, "profiles/educator/dc-progress.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.filter(draft=False).order_by('id'),
        'memberships': request.user.membership_set.all()
    })
