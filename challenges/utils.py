from .models import Stage

def get_stage_for_progress(progress, default=Stage.plan):
    try:
        return Stage(progress.comments.filter(user_id=progress.owner_id).order_by("-created")[0].stage)
    except IndexError:
        return default
