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
        'units': Unit.objects.filter(draft=False).order_by('id'),
        'memberships': request.user.memberships.all()
    })
