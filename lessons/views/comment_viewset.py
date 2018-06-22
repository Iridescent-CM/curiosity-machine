from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from ..models import *
from ..permissions import CommentPermission
from ..serializers import *

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    renderer_classes = (JSONRenderer, )
    permission_classes = (CommentPermission, )

    def get_queryset(self):
        queryset = Comment.objects.all()
        progress_filter = self.request.query_params.get('lesson_progress', None)
        if progress_filter is not None:
            queryset = queryset.filter(lesson_progress_id=progress_filter)
        return queryset

