from collections import OrderedDict
from django.urls import reverse
from .models import *

class TabbedLesson(object):

    config = OrderedDict({
        "start": "Start",
        "inspiration": "Inspiration",
        "plan": "Plan",
        "build": "Build Test Redesign",
        "reflect":"Reflect",
        "further": "Further learning",
    })

    def __init__(self, lesson, current_page, progress=None):
        self.lesson = lesson
        self.progress = progress
        self.current_page = current_page or "start"

    def __getattr__(self, name):
        return getattr(self.lesson, name)

    @property
    def valid(self):
        return self.current_page in self.config

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

    @property
    def next_lesson_url(self):
        next_lesson = Lesson.objects.filter(order=self.lesson.order + 1).first()

        if not next_lesson:
            return None

        if self.progress:
            return reverse("lessons:lesson-progress-find-or-create") + "?lesson=%d" % next_lesson.id
        else:
            return reverse("lessons:lesson-detail", kwargs={"pk": next_lesson.id})
