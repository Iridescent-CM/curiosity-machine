from functools import wraps
from django.core.exceptions import PermissionDenied
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
