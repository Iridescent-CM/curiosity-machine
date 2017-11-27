from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import UserRole

def is_role(user, role):
    return hasattr(user, "extra") and user.extra.role == role.value

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
