from rest_framework import permissions
from .models import *

class ProgressPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff

class CommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'pk' in view.kwargs:
            return True     # let object permission handle it

        progress_pk = request.query_params.get('lesson_progress', request.data.get('lesson_progress', None))
        progress = Progress.objects.filter(id=progress_pk).first()

        if progress and ProgressPermission().has_object_permission(request, view, progress):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff
