from curiositymachine import signals
from django.dispatch import receiver
from cmemails import deliver_email
from challenges.models import Stage

@receiver(signals.student.started_first_project)
def student_started_first_project(sender, progress, **kwargs):
    deliver_email('first_project', sender.profile)

@receiver(signals.mentor.approved_project_for_gallery)
def mentor_approved_project_for_gallery(sender, example, **kwargs):
    deliver_email('publish', example.progress.student.profile, progress=example.progress)

@receiver(signals.mentor.posted_comment)
def mentor_posted_comment(sender, comment, **kwargs):
    progress = comment.challenge_progress
    deliver_email('mentor_responded', progress.student.profile, progress=progress, mentor=progress.mentor.profile)

@receiver(signals.student.posted_comment)
def student_posted_comment(sender, comment, **kwargs):
    progress = comment.challenge_progress

    if not progress.mentor:
        return

    if comment.stage != Stage.reflect.value:
        deliver_email('student_responded', progress.mentor.profile, progress=progress, student=progress.student.profile)
    elif comment.stage == Stage.reflect.value and comment.image:
        deliver_email('student_completed', progress.mentor.profile, student=progress.student.profile, progress=progress)
    else:
        # TODO: figure out the right email and send it here
        pass