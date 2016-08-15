from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Membership

def enforce_membership_challenge_access(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        challenge_id = kwargs.get('challenge_id')
        if Membership.filter_by_challenge_access(request.user, [challenge_id]):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner