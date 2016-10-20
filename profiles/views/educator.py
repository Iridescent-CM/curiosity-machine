from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from ..forms import educator as forms
from ..decorators import membership_selection
from challenges.models import Challenge
from units.models import Unit
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
@membership_selection
def home(request, membership_selection=None):
    core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

    membership_challenges = []
    membership = None
    if membership_selection and membership_selection["selected"]:
        membership = request.user.membership_set.get(pk=membership_selection["selected"]["id"])
        membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')

    return render(request, "profiles/educator/dashboard/challenges.html", {
        "membership": membership,
        "membership_challenges": membership_challenges,
        "core_challenges": core_challenges,
        "membership_selection": membership_selection,
    })

@educator_only
@login_required
@membership_selection
def students_dashboard(request, membership_selection=None):
    return render(request, "profiles/educator/dashboard/students.html", {
        "membership_selection": membership_selection,
    })

@educator_only
@login_required
@membership_selection
def guides_dashboard(request, membership_selection=None):
    units = Unit.objects.filter(listed=True).select_related('image')
    return render(request, "profiles/educator/dashboard/guides.html", {
        "units": units,
        "membership_selection": membership_selection,
    })
