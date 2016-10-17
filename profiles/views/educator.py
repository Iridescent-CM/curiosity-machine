from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from profiles.forms import educator as forms
from challenges.models import Challenge
from curiositymachine.decorators import educator_only
from curiositymachine.views.generic import UserJoinView
from django.utils.functional import lazy

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
    challenges = Challenge.objects.filter(draft=False, core=True).select_related('image')
    return render(request, "profiles/educator/dashboard/challenges.html", {
        "challenges": challenges,
    })

@educator_only
@login_required
def students_dashboard(request):
    return render(request, "profiles/educator/dashboard/students.html", {})

@educator_only
@login_required
def guides_dashboard(request):
    return render(request, "profiles/educator/dashboard/guides.html", {})
