from django.shortcuts import render, get_object_or_404
import django.contrib.auth
User = django.contrib.auth.get_user_model()
from django.http import HttpResponseRedirect
from profiles.models import Profile
from profiles.forms import JoinForm


def join(request):
    if request.method == 'POST':
        form = JoinForm(request=request, data=request.POST) 
        if form.is_valid():
            return HttpResponseRedirect(request.user.get_absolute_url())
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(request.user.get_absolute_url())
        form = JoinForm()
    template_values = {
        'form': form,
    }

    return render(request, 'join.html', template_values)


def profile_details(request, email):
    '''
    Page for viewing a users profile
    '''
    user = get_object_or_404(User, email=email)
    # profile = get_object_or_404(Profile, user=user)


    template_values = {
        'user': user,
    }

    return render(request, 'profile_details.html', template_values)