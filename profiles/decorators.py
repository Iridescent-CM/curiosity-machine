from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
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

def not_for_role(*args, **kwargs):
    viewname = kwargs.get('redirect')
    roles = args
    def decorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            is_any = list(role for role in roles if is_role(request.user, role))
            if request.user.is_authenticated() and is_any:
                if viewname:
                    return HttpResponseRedirect(reverse(viewname))
                else:
                    raise PermissionDenied
            else:
                return view(request, *args, **kwargs)
        return inner
    return decorator
