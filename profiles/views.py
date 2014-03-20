from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from profiles.models import Profile
from profiles.forms import JoinForm


def join(request):
    if request.method == 'POST':
        form = JoinForm(request=request, data=request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            user = User()
            user.email = data['email']
            user.username = data['username']
            user.first_name = data['first_name']
            user.is_active = True
            user.set_password(data['password'])
            try:
                user.save()
            except IntegrityError:
                raise forms.ValidationError('Username has already been used')
            profile = Profile()
            profile.is_mentor = False
            profile.user = user
            profile.birthday = data['birthday']
            profile.nickname = data['nickname']
            profile.city = data['city']
            profile.parent_first_name = data['parent_first_name']
            profile.parent_last_name = data['parent_last_name']
            profile.save()
            user = auth.authenticate(username=data['username'], password=data['password'])
            auth.login(request, user)
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(request.user.profile.get_absolute_url())
        form = JoinForm()
    template_values = {
        'form': form,
    }

    return render(request, 'join.html', template_values)


def student_profile_details(request, username):
    '''
    Page for viewing a users profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=False)


    template_values = {
        'user': user,
        'profile': profile,
    }

    return render(request, 'profile_details.html', template_values)

def mentor_profile_details(request, username):
    '''
    Page for viewing a users profile
    '''
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user, is_mentor=True)


    template_values = {
        'user': user,
        'profile': profile,
    }

    return render(request, 'profile_details.html', template_values)