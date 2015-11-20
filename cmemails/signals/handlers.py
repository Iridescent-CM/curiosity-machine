from curiositymachine import signals
from django.dispatch import receiver
from cmemails import deliver_email
from challenges.models import Stage

@receiver(signals.started_first_project)
def started_first_project(sender, progress, **kwargs):
    deliver_email('first_project', sender.profile)

@receiver(signals.approved_project_for_gallery)
def approved_project_for_gallery(sender, example, **kwargs):
    deliver_email('publish', example.progress.student.profile, progress=example.progress)

@receiver(signals.approved_project_for_reflection)
def approved_project_for_reflection(sender, progress, **kwargs):
    deliver_email('project_completion', progress.student.profile, progress=progress, stage=Stage.reflect.name)

@receiver(signals.posted_comment)
def posted_comment(sender, comment, **kwargs):
    progress = comment.challenge_progress

    if not progress.mentor:
        return

    if sender.profile.is_mentor:
        deliver_email('mentor_responded', progress.student.profile, progress=progress, mentor=progress.mentor.profile)
    elif sender.profile.is_student:
        if comment.stage != Stage.reflect.value:
            deliver_email('student_responded', progress.mentor.profile, progress=progress, student=progress.student.profile)
        elif comment.stage == Stage.reflect.value and comment.image:
            deliver_email('student_completed', progress.mentor.profile, student=progress.student.profile, progress=progress)
        else:
            # TODO: figure out the right email and send it here
            pass