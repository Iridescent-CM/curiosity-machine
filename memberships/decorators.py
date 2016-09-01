from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Membership, Member

def enforce_membership_challenge_access(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        challenge_id = kwargs.get('challenge_id')
        if Membership.filter_by_challenge_access(request.user, [challenge_id]):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

def members_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            membership_id = kwargs.get('membership_id')
            if membership_id and Member.objects.filter(user=request.user, membership__id=membership_id).exists():
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return inner
