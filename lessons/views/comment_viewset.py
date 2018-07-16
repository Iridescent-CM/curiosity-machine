from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from ..models import *
from ..permissions import CommentPermission
from ..serializers import *

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    renderer_classes = (JSONRenderer, )
    permission_classes = (CommentPermission, )

    filters = {
        'lesson_progress': 'lesson_progress_id',
        'role': 'role',
    }

    def get_queryset(self):
        queryset = Comment.objects.all()
        for qparam, attr in self.filters.items():
            val = self.request.query_params.get(qparam, None)
            if val is not None:
                queryset = queryset.filter(**{attr: val})
        return queryset
