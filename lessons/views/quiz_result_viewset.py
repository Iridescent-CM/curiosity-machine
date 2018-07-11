from rest_framework import mixins, viewsets
from rest_framework.renderers import JSONRenderer
from ..models import *
from ..serializers import *

class QuizResultViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = QuizResultSerializer
    renderer_classes = (JSONRenderer, )

    def get_queryset(self):
        try:
            quiz = self.request.query_params.get('quiz')
            taker = self.request.query_params.get('taker')
        except KeyError:
            raise Http404

        return QuizResult.objects.filter(quiz_id=quiz, taker_id=taker)
