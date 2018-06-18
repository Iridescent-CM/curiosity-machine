NOT_STARTED = "not-started"
COMPLETED = "completed"
STARTED = "started"

class LearningSet:
    """
    objects can be e.g. Challenges or Lessons
    user_progresses represents progress on the learning object, and must implement:
        .object_id - id of the associated learning object
        .completed - completed status of progress

    Decorated states (unless the code has changed and this comment wasn't updated):
        NOT_STARTED:    a progress doesn't even exist for this object
        STARTED:        a progress exists but it is not completed
        COMPLETED:      a progress exists and is completed
    """

    def __init__(self, objects, user_progresses=[]):
        self.objects = self._decorate(objects, user_progresses)

    def _decorate(self, objects, progresses=[]):
        prog_by_object_id = {p.object_id: p for p in progresses}

        for obj in objects:
            obj.state = NOT_STARTED
            if obj.id in prog_by_object_id:
                progress = prog_by_object_id[obj.id]
                if progress.completed:
                    obj.state = COMPLETED
                else:
                    obj.state = STARTED

        return objects

    @property
    def stats(self):
        stats = {}
        objects = self.objects
        stats["total"] = len(objects)
        stats["completed"] = len([o for o in objects if getattr(o, "state", None) == COMPLETED])
        stats["percent_complete"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        return stats

    @property
    def is_complete(self):
        return self.stats["percent_complete"] == 100

    def has_object(self, obj_or_id):
        obj_id = obj_or_id if type(obj_or_id) == int else obj_or_id.id
        return obj_id in [o.id for o in self.objects]
