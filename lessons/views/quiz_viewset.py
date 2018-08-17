from rest_framework import mixins, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from ..models import *
from ..serializers import *

class QuizViewSet(viewsets.GenericViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    renderer_classes = (JSONRenderer, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        taker = self.request.query_params.get('taker', None)
        if taker:
            latest = QuizResult.objects.filter(quiz=instance, taker_id=taker).order_by('-created_at').first()
            if latest:
                serializer = QuizAndResultSerializer(latest)

        return Response(serializer.data)
