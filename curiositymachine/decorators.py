from functools import wraps
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
from memberships.models import Membership

def anonymous_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('root'))
        else:
            return view(request, *args, **kwargs)
    return inner

def unapproved_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.extra.is_approved:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('root'))
    return inner

def current_user(view):
    @wraps(view)
    def inner(request, challenge_id, username, *args, **kwargs):
        if request.user.username == username:
            return view(request, challenge_id, username, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('challenges:preview_inspiration', kwargs={'challenge_id': challenge_id}))
    return inner

def current_user_or_approved_viewer(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        username = kwargs.get('username')
        challenge_id = kwargs.get('challenge_id')
        if (request.user.is_staff
                or request.user.username == username
                or (not request.user.extra.is_student and Membership.share_membership(request.user.username, username))):
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('challenges:preview_inspiration', kwargs={'challenge_id': challenge_id}))
    return inner

#also permits staff
def educator_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.extra.is_educator):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

def student_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.extra.is_student):
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

def whitelist(*listnames):
    """
    Add view to named whitelist(s)
    """
    def decorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            return view(request, *args, **kwargs)
        inner.whitelist = listnames
        return inner
    return decorator
