from .models import Stage

def get_stage_for_progress(progress, default=Stage.plan):
    try:
        # find most recent activity and use its stage
        stage = progress.comments.order_by("-created")[0]
    except IndexError:
        # if no activity, use default
        return default
