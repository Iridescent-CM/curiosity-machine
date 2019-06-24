from django.http import HttpResponseRedirect, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from curiositymachine.decorators import whitelist
from ..models import *
from ..presenters import *

public = whitelist('public')

class LessonViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.filter(draft=False)
    renderer_classes = (TemplateHTMLRenderer, )

    def get_page_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', None)
        lesson = TabbedLesson(self.object, self.page)

        if not lesson.valid:
            raise Http404

        return Response({'lesson': lesson}, template_name=self.get_page_template_names)

    def list(self, request):
        lessons = self.queryset
        return Response({'lessons': lessons}, template_name="lessons/lessons.html")

lessons = LessonViewSet.as_view({'get':'list'})