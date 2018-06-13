from django.http import HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from .. import config

class LessonViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', list(config.LESSON_NAV.keys())[0])
        return Response(
            {
                'lesson': self.object,
                'subnav': config.LESSON_NAV,
                'active': self.page,
                'content': getattr(self.object, self.page, None),
            },
        )

    @action(methods=['get'], detail=True)
    def progress(self, request, pk=None):
        progress, created = Progress.objects.get_or_create(owner_id=request.user.id, lesson_id=pk)
        return HttpResponseRedirect(reverse("lessons:lesson-progress-detail", kwargs={"pk": progress.id}))
