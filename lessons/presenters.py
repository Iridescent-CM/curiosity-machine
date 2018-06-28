from collections import OrderedDict

class TabbedLesson(object):

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
        self.current_page = current_page or "start"

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
