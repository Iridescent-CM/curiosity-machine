from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Membership

def owners_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        group_id = kwargs['group_id']
        if (request.user.is_authenticated() and Membership.user_owns_group(request.user, group_id)):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner
