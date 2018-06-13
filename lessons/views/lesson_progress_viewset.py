from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from .. import config

class LessonProgressViewSet(viewsets.GenericViewSet):
    queryset = Progress.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', list(config.LESSON_NAV.keys())[0])
        return Response(
            {
                'lesson': self.object.lesson,
                'progress': self.object,
                'subnav': config.LESSON_NAV,
                'active': self.page,
                'content': getattr(self.object.lesson, self.page, None),
            },
        )
