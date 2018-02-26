from challenges.models import Challenge, Progress
from challenges.models import Stage as CommentStage
from django.conf import settings
from units.models import Unit

def get_stages(user=None):
    return [Stage.from_config(num, user=user) for num in settings.AICHALLENGE_STAGES]

class Stage:
    @classmethod
    def from_config(cls, stagenum, user=None, config=None):
        config = config or settings.AICHALLENGE_STAGES[stagenum]

        challenges = sorted(
            Challenge.objects.filter(id__in=config['challenges']),
            key=lambda c: config['challenges'].index(c.id)
        )

        progresses = None
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

    def __init__(self, number, challenges, units, user_progresses=None):
        self.number = number
        self.challenges = self._decorate(challenges, user_progresses)
        self.units = units

    def _decorate(self, challenges, progresses=None):
        if not progresses:
            return challenges

        prog_by_challenge_id = {p.challenge_id: p for p in progresses}

        for challenge in challenges:
            challenge.state = "not-started"
            if challenge.id in prog_by_challenge_id:
                progress = prog_by_challenge_id[challenge.id]
                if progress.completed:
                    challenge.state = "completed"
                else:
                    challenge.state = "started"

        return challenges

    @property
    def stats(self):
        stats = {}
        challenges = self.challenges
        stats["total"] = len(challenges)
        stats["completed"] = len([c for c in challenges if getattr(c, "state", None) == "completed"])
        stats["percent_complete"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        return stats

    @property
    def is_complete(self):
        return self.stats["percent_complete"] == 100

    def has_challenge(self, challenge_or_id):
        challenge_id = challenge_or_id if type(challenge_or_id) == int else challenge_or_id.id
        return challenge_id in [c.id for c in self.challenges]
