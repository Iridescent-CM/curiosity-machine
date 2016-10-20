from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import Http404
from profiles.models import ParentConnection

def parents_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated() and (request.user.profile.is_parent or request.user.is_staff):
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return inner

def connected_parent_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        connection_id = kwargs.get('connection_id')
        if request.user.is_authenticated() and connection_id:
            connection = ParentConnection.objects.filter(pk=connection_id, removed=False).first()
            if connection and request.user.profile == connection.parent_profile:
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return inner

def connection_active(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        connection_id = kwargs.get('connection_id')
        if request.user.is_authenticated() and connection_id:
            connection = ParentConnection.objects.filter(pk=connection_id, removed=False).first()
            if connection and connection.active:
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return inner

def active_connected_parent_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        connection_id = kwargs.get('connection_id')
        if request.user.is_authenticated() and connection_id:
            connection = ParentConnection.objects.filter(pk=connection_id, removed=False, active=True).first()
            if connection and request.user.profile == connection.parent_profile:
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return inner

def connected_child_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        connection_id = kwargs.get('connection_id')
        if request.user.is_authenticated() and connection_id:
            connection = ParentConnection.objects.filter(pk=connection_id, removed=False).first()
            if connection and request.user.profile == connection.child_profile:
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return inner

def membership_selection(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        memberships = request.user.membership_set.values('id', 'display_name')
        active = None
        if memberships:
            active = None

            qparam = request.GET.get('m')
            if qparam:
                try:
                    qparam = int(qparam)
                    active = next(d for d in memberships if d['id'] == qparam)
                    request.session['active_membership'] = qparam
                except:
                    raise Http404

            elif "active_membership" in request.session:
                try:
                    active = next(d for d in memberships if d['id'] == request.session.get('active_membership'))
                except:
                    del request.session['active_membership']
                    active = memberships[0]

            else:
                active = memberships[0]

        kwargs['membership_selection'] = {
            "count": len(memberships),
            "selected": active,
            "all": memberships,
            "names": ", ".join([o["display_name"] for o in memberships]) or "None"
        }
        return view(request, *args, **kwargs)
    return inner
