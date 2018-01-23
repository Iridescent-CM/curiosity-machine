from challenges.models import Challenge, Progress
from django.conf import settings
from units.models import Unit

class Stage:
    def __init__(self, stagenum, *args, **kwargs):
        self.number = stagenum
        self.config = settings.AICHALLENGE_STAGES[stagenum]

    @property
    def challenges(self):
        return sorted(
            Challenge.objects.filter(id__in=self.config['challenges']),
            key=lambda c: self.config['challenges'].index(c.id)
        )

    @property
    def units(self):
        return sorted(
            Unit.objects.filter(id__in=self.config['units']),
            key=lambda u: self.config['units'].index(u.id)
        )

    @property
    def stats(self):
        stats = {}
        stats["total"] = len(self.challenges)
        # garbage data for now
        import random
        if not hasattr(self, "completed"):
            self.completed = random.randint(0, stats["total"])
        stats["completed"] = self.completed
        # end garbage
        stats["percent_complete"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        return stats

    def progress(self, user):
        progresses = Progress.objects.filter(owner=user, challenge_id__in=self.config['challenges'])
        prog_by_challenge_id = {p.challenge_id: p for p in progresses}

        challenges = self.challenges
        for challenge in challenges:
            if challenge.id in prog_by_challenge_id:
                # decorate here with level of progress for visual representation
                pass

        return challenges
