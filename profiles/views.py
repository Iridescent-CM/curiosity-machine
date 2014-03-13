from django.shortcuts import render
import django.contrib.auth
User = django.contrib.auth.get_user_model()
from django.shortcuts import get_object_or_404
from profiles.models import Profile

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