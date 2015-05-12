from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from profiles.forms import parent as forms

@transaction.atomic
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
def home(request):
    return render(request, "profiles/parent/home.html", {})
