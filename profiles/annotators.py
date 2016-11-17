from challenges.models import Stage

class UserCommentSummary():
    def __init__(self, comments, user_id):
        self.comments = [c for c in comments if c.user_id == user_id]

    def annotate(self, obj):
        obj.total_user_comments = len(self.comments)
        obj.latest_user_comment = max(self.comments, key=lambda o: o.created) if self.comments else None

        counts_by_stage = [0, 0, 0, 0, 0];
        for comment in self.comments:
            counts_by_stage[comment.stage] = counts_by_stage[comment.stage] + 1
        obj.user_comment_counts_by_stage = counts_by_stage[1:] # inspiration stage can't have comments

        obj.complete = counts_by_stage[Stage.reflect.value] != 0

        return obj

