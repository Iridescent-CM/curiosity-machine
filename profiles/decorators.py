from functools import wraps
from django.core.exceptions import PermissionDenied

def parents_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated() and (request.user.profile.is_parent or request.user.is_staff):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner
