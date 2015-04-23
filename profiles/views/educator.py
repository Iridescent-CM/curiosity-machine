from django.shortcuts import render
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

@feature_flag('enable_educators')
@transaction.atomic
def join(request):
    if request.method == 'POST':
        userForm = forms.UserCreationForm(request.POST, prefix='user')
        profileForm = forms.ProfileChangeForm(request.POST, prefix='profile')
        if userForm.is_valid() and profileForm.is_valid():
            user = userForm.save()
            profileForm = forms.ProfileChangeForm(request.POST,
                prefix='profile',
                instance=user.profile
            )
            profileForm.save()
            user = auth.authenticate(
                username=userForm.cleaned_data['username'],
                password=userForm.cleaned_data['password']
            )
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'profiles/educator/join.html', {
                'userForm': userForm,
                'profileForm': profileForm
            })
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            userForm = forms.UserCreationForm(prefix='user')
            profileForm = forms.ProfileChangeForm(prefix='profile')
            return render(request, 'profiles/educator/join.html', {
                'userForm': userForm,
                'profileForm': profileForm
            })

@feature_flag('enable_educators')
@educator_only
@login_required
def home(request):
    return render(request, "profiles/educator/home.html", {
        'form': GroupForm(),
        'groups': request.user.cm_groups.all(),
        'units': Unit.objects.all().order_by('id'),
    })
