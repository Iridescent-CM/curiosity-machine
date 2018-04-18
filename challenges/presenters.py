class ChallengeSet:
    def __init__(self, challenges, user_progresses=None):
        self.challenges = self._decorate(challenges, user_progresses)

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
