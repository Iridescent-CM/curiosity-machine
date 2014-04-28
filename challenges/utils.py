from .models import Stage

def get_stage_for_progress(progress, default=Stage.plan):
    try:
        # find most recent activity and use its stage
        return Stage(progress.comments.order_by("-created")[0].stage)
    except IndexError:
        # if no activity, use default
        return default
