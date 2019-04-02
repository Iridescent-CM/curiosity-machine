from lessons.models import Lesson, Progress as LessonProgress

NOT_STARTED = "not-started"
COMPLETED = "completed"
STARTED = "started"

class LearningSet:
    """
    Decorated states (unless the code has changed and this comment wasn't updated):
        NOT_STARTED:    a progress doesn't even exist for this lesson
        STARTED:        a progress exists but it is not completed
        COMPLETED:      a progress exists and is completed
    """

    @classmethod
    def from_config(self, user=None, config=None):
        self.lessons = Lesson.objects.filter(draft=False)
        if user:
            self.progresses = LessonProgress.objects.filter(
                owner=user
            )
        self._decorate(self)
        return self


    def _decorate(self):        
        prog_by_lesson_id = {p.lesson_id: p for p in self.progresses}

        for lesson in self.lessons:
            lesson.state = NOT_STARTED
            if lesson.id in prog_by_lesson_id:
                progress = prog_by_lesson_id[lesson.id]
                if progress.completed:
                    lesson.state = COMPLETED
                else:
                    lesson.state = STARTED

        return self.lessons

    @property
    def stats(self):
        stats = {}
        stats["total"] = len(self.lessons)
        stats["completed"] = len([l for l in self.lessons if getattr(l, "state", None) == COMPLETED])
        stats["percent_complete"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        return stats

    @property
    def is_complete(self):
        return self.stats["percent_complete"] == 100

    def has_object(self, obj_or_id):
        obj_id = obj_or_id if type(obj_or_id) == int else obj_or_id.id
        return obj_id in [l.id for l in self.lessons]
