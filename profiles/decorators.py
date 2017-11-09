from functools import wraps
from django.core.exceptions import PermissionDenied

# TODO: do this with enum, not strings?
def is_role(user, role):
    return hasattr(user, "extra") and getattr(user.extra, "is_%s" % role)

def only_for_role(*args):
    roles = args
    def decorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            is_any = list(role for role in roles if is_role(request.user, role))
            if request.user.is_authenticated() and (request.user.is_staff or is_any):
                return view(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return inner
    return decorator
