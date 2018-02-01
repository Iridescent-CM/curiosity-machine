from challenges.models import Challenge, Progress
from challenges.models import Stage as CommentStage
from django.conf import settings
from units.models import Unit

class Stage:
    def __init__(self, stagenum, user=None, *args, **kwargs):
        self.number = stagenum
        self.user = user
        self.config = settings.AICHALLENGE_STAGES[stagenum]

    @property
    def challenges(self):
        challenges = sorted(
            Challenge.objects.filter(id__in=self.config['challenges']),
            key=lambda c: self.config['challenges'].index(c.id)
        )

        if self.user:
            progresses = Progress.objects.filter(
                owner=self.user,
                challenge_id__in=self.config['challenges']
            )
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
    def units(self):
        return sorted(
            Unit.objects.filter(id__in=self.config['units']),
            key=lambda u: self.config['units'].index(u.id)
        )

    @property
    def stats(self):
        stats = {}
        challenges = self.challenges
        stats["total"] = len(challenges)
        stats["completed"] = len([c for c in challenges if c.state == "completed"])
        stats["percent_complete"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        return stats
