from curiositymachine import signals
from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from cmemails import deliver_email, send
from challenges.models import Stage
import urllib.parse

@receiver(signals.created_account)
def deliver_welcome_email(sender, **kwargs):
    if sender.profile.is_mentor:
        send(template_name='mentor-welcome-email', to=sender, cc=settings.MENTOR_RELATIONSHIP_MANAGERS)
    else:
        deliver_email('welcome', sender.profile)

@receiver(signals.underage_activation_confirmed)
def underage_activation_confirmed(sender, account, **kwargs):
    deliver_email('activation_confirmation', account.profile)

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
            path = reverse('challenges:challenge_progress', kwargs={
                "challenge_id": progress.challenge.id,
                "username": sender.username,
                "stage": Stage(comment.stage).name
            })
            send(template_name='mentor-student-responded-to-feedback', to=progress.mentor, merge_vars={
                "studentname": sender.username,
                "url": urllib.parse.urljoin(settings.SITE_URL, path)
            })
        elif comment.stage == Stage.reflect.value and comment.image:
            deliver_email('student_completed', progress.mentor.profile, student=progress.student.profile, progress=progress)
        else:
            # TODO: figure out the right email and send it here
            pass

@receiver(signals.approved_training_task)
def approved_training_task(sender, user, task, **kwargs):
    if task.completion_email_template:
        send(template_name=task.completion_email_template, to=user)

@receiver(signals.completed_training)
def completed_training(sender, approver, **kwargs):
    send(template_name='mentor-account-approved', to=sender)