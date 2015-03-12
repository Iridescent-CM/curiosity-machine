from functools import wraps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings

def mentor_or_current_user(view):
    @wraps(view)
    def inner(request, challenge_id, username, *args, **kwargs):
        if request.user.profile.is_mentor or request.user.username == username: 
            return view(request, challenge_id, username, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('challenges:challenge', kwargs={'challenge_id': challenge_id}))
    return inner

#also permits staff
def educator_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_staff or request.user.profile.is_educator:
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

def student_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_staff or request.user.profile.is_student:
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

# also permits staff
def mentor_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_staff or request.user.profile.is_mentor:
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

def feature_flag(flag):
    flag = flag.lower()
    def decorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            if flag in settings.FEATURE_FLAGS and settings.FEATURE_FLAGS[flag]:
                return view(request, *args, **kwargs)
            else:
                raise Http404
        return inner
    return decorator
