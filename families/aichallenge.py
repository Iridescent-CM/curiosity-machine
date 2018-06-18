from challenges.models import Challenge, Progress
from challenges.models import Stage as CommentStage
from curiositymachine.presenters import LearningSet
from django.conf import settings
from lessons.models import Lesson
from lessons.models import Progress as LessonProgress
from units.models import Unit

def get_stages(user=None):
    return [Stage.from_config(num, user=user) for num in settings.AICHALLENGE_STAGES]

class Stage(LearningSet):
    @classmethod
    def from_config(cls, stagenum, user=None, config=None):
        # FIXME: this top if/else is kind of weird
        if stagenum == 3:

            lessons = Lesson.objects.all()

            progresses = []
            if user:
                progresses = LessonProgress.objects.filter(
                    owner=user
                )

            return cls(stagenum, lessons, [], progresses)
        else:
            config = config or settings.AICHALLENGE_STAGES[stagenum]

            challenges = sorted(
                Challenge.objects.filter(id__in=config['challenges']),
                key=lambda c: config['challenges'].index(c.id)
            )

            progresses = []
            if user:
                progresses = Progress.objects.filter(
                    owner=user,
                    challenge_id__in=config['challenges']
                )

            units = sorted(
                Unit.objects.filter(id__in=config['units']),
                key=lambda u: config['units'].index(u.id)
            )

            return cls(stagenum, challenges, units, progresses)

    def __init__(self, number, challenges, units, user_progresses=[]):
        super().__init__(challenges, user_progresses)
        self.number = number
        self.units = units
