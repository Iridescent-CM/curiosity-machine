from functools import wraps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

def mentor_or_current_student(view):
    @wraps(view)
    def inner(request, challenge_id, username, *args, **kwargs):
        if request.user.profile.is_mentor or request.user.username == username: 
            return view(request, challenge_id, username, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('challenges:challenge', kwargs={'challenge_id': challenge_id}))
    return inner

def mentor_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.profile.is_mentor:
            return view(request, *args, **kwargs)
        else:
            return HttpResponse("Access denied", status=403)
    return inner
