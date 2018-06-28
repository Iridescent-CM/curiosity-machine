from django.http import Http404, HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from ..permissions import ProgressPermission
from ..presenters import *

class LessonProgressViewSet(viewsets.GenericViewSet):
    queryset = Progress.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )
    permission_classes = (ProgressPermission, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', None)
        return Response(
            {
                'lesson': TabbedLesson(self.object.lesson, self.page),
                'progress': self.object,
            },
        )

    @action(methods=['get'], detail=False)
    def find_or_create(self, request):
        lesson_id = request.query_params.get('lesson', None)
        if not lesson_id:
            raise Http404

        progress, created = Progress.objects.get_or_create(owner_id=request.user.id, lesson_id=lesson_id)
        return HttpResponseRedirect(reverse("lessons:lesson-progress-detail", kwargs={"pk": progress.id}))

