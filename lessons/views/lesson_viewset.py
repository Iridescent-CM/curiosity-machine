from django.http import HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from ..presenters import *

class LessonViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.filter(draft=False)
    renderer_classes = (TemplateHTMLRenderer, )
    
    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', None)
        lesson = TabbedLesson(self.object, self.page)

        if not lesson.valid:
            raise Http404

        try:
            template_name = "lessons/%s.html" % self.page
            get_template("lessons/%s.html" % self.page) # check if a specific page template exists
        except TemplateDoesNotExist:
            template_name = "lessons/page.html"

        return Response({'lesson': lesson}, template_name=template_name)

    def list(self, request):
        lessons = self.get_queryset()
        return Response({'lessons': lessons}, template_name="lessons/lessons.html")