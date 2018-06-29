from django.http import HttpResponseRedirect, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from ..presenters import *

class LessonViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', None)
        lesson = TabbedLesson(self.object, self.page)

        if not lesson.valid:
            raise Http404

        return Response({'lesson': lesson})
