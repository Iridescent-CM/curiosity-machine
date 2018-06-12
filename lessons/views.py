from collections import OrderedDict
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from rest_framework import serializers
from rest_framework import viewsets
from .models import *

LESSON_NAV = OrderedDict({
    "inspiration": {
        "text": "Inspiration",
    },
    "plan": {
        "text": "Plan",
    },
    "build": {
        "text": "Build Test Redesign"
    },
    "reflect": {
        "text": "Reflect"
    },
    "further": {
        "text": "Further learning"
    }
})

class PageView(DetailView):
    model = Lesson
    context_object_name = "lesson"

    def get(self, request, *args, **kwargs):
        page = kwargs.pop('page')
        self.page = page.lower()
        if self.page not in LESSON_NAV:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/base.html",]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            subnav=LESSON_NAV,
            active=self.page,
            content=getattr(self.object, self.page, None)
        )

show_page = staff_member_required(PageView.as_view())

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from lessons.models import *
from django.http import HttpResponse, HttpResponseRedirect

class LessonViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', list(LESSON_NAV.keys())[0])
        return Response(
            {
                'lesson': self.object,
                'subnav': LESSON_NAV,
                'active': self.page,
                'content': getattr(self.object, self.page, None),
            },
        )

    @action(methods=['get'], detail=True)
    def progress(self, request, pk=None):
        progress, created = Progress.objects.get_or_create(owner_id=request.user.id, lesson_id=pk)
        return HttpResponseRedirect(reverse("lessons:lesson-progress-detail", kwargs={"pk": progress.id}))

class LessonProgressViewSet(viewsets.GenericViewSet):
    queryset = Progress.objects.all()
    renderer_classes = (TemplateHTMLRenderer, )

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/page.html",]

    def retrieve(self, request, pk=None):
        self.object = self.get_object()
        self.page = self.request.query_params.get('page', list(LESSON_NAV.keys())[0])
        return Response(
            {
                'lesson': self.object.lesson,
                'progress': self.object,
                'subnav': LESSON_NAV,
                'active': self.page,
                'content': getattr(self.object.lesson, self.page, None),
            },
        )
