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
        self.update_tab_status(current_page)

    def __getattr__(self, name):
        return getattr(self.lesson, name)

    def update_tab_status(self, current_page):
        self.update_visited_pages(current_page)
        self.update_build_status()
        self.update_reflect_status()
        if self.progress:
            self.progress.save()

    def update_visited_pages(self, current_page):
        if self.progress:
            if self.progress.start == STARTED:
                self.progress.start = COMPLETED
            if self.progress.inspiration == STARTED:
                self.progress.inspiration = COMPLETED
            if self.progress.plan == STARTED:
                self.progress.plan = COMPLETED
            if self.progress.further == STARTED:
                self.progress.further = COMPLETED
            if getattr(self.progress, self.current_page) == NOT_STARTED:
                setattr(self.progress, self.current_page, STARTED)

    def update_build_status(self):
        if self.progress:
            if self.progress.comment_set.all().exists():
                self.progress.build = COMPLETED
            elif self.progress.build == COMPLETED:
                self.progress.build = STARTED

    def update_reflect_status(self):
        if self.quiz and self.quiz.quizresult_set.exists():
            setattr(self.progress, "reflect", COMPLETED)
    
    def progress_warning(self):
        if self.current_page == "build":
            return "You haven't submitted anything on the Build section."
        if self.current_page == "reflect" or self.current_page == "further":
            return "Looks like you're missing something."

    def show_warning(self):
        return ((self.current_page == "build" and self.progress.build != COMPLETED)
            or (self.current_page == "reflect" and self.progress.reflect != COMPLETED)
            or (self.current_page == "further" and (self.progress.build != COMPLETED or self.progress.reflect != COMPLETED)))

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

