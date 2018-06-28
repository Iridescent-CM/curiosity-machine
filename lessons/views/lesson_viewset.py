from collections import OrderedDict
from django.http import HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from ..models import *
from .. import config

class TabbedLesson:

    config = OrderedDict({
        "start": "Start",
        "inspiration": "Inspiration",
        "plan": "Plan",
        "build": "Build Test Redesign",
        "reflect":"Reflect",
        "further": "Further learning",
    })

    def __init__(self, lesson, current_page):
        self.lesson = lesson
        self.current_page = current_page

    @property
    def title(self):
        return self.lesson.title

    @property
    def tabs(self):
        return [
            {
                "param": k,
                "active": k == self.current_page,
                "name": v
            }
            for k, v in self.config.items()
        ]

    @property
    def active_tab(self):
        return {
            "param": self.current_page,
            "name": self.config.get(self.current_page),
            "content": getattr(self.lesson, self.current_page, ""),
        }

    @property
    def prev_tab(self):
        return self.get_relative_tab(-1)

    @property
    def next_tab(self):
        return self.get_relative_tab(1)

    def get_relative_tab(self, offset):
        keys = list(self.config.keys())
        idx = keys.index(self.current_page) + offset
        if idx < 0 or idx >= len(keys):
            return None

        key = keys[idx]
        return {
            "name": self.config[key],
            "param": key
        }

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
                'lesson': TabbedLesson(self.object, self.page)
            },
        )
