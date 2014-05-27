from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def root_redirect(request):
    # redirect to home if logged in unless you are a student with no challenges
    if request.user.is_authenticated() and (request.user.profile.is_mentor or request.user.progresses.exists()):
        return HttpResponseRedirect(reverse('profiles:home'))
    else:
        return HttpResponseRedirect(reverse('challenges:challenges'))