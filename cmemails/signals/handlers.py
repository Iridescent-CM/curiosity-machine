from curiositymachine import signals
from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from cmemails import deliver_email, send, subscribe
from cmemails.mandrill import url_for_template
from challenges.models import Stage
import urllib.parse
import re

@receiver(signals.created_account)
def send_welcome_email(sender, **kwargs):
    if sender.profile.is_mentor:
        send(template_name='mentor-welcome-email', to=sender, cc=settings.MENTOR_RELATIONSHIP_MANAGERS)
    else:
        deliver_email('welcome', sender.profile)
    subscribe(sender)

@receiver(signals.underage_activation_confirmed)
def send_activation_confirmation(sender, account, **kwargs):
    deliver_email('activation_confirmation', account.profile)

@receiver(signals.started_first_project)
def send_first_project_encouragement(sender, progress, **kwargs):
    deliver_email('first_project', sender.profile)

@receiver(signals.approved_project_for_gallery)
def send_example_publication_notice(sender, example, **kwargs):
    deliver_email('publish', example.progress.student.profile, progress=example.progress)

@receiver(signals.progress_considered_complete)
def send_mentor_progress_completion_notice(sender, progress, **kwargs):
    if progress.mentor:
        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": sender.username
        })
        send(template_name='mentor-student-completed-project', to=progress.mentor, merge_vars={
            "studentname": progress.student.username,
            "progress_url": url_for_template(path),
        })

@receiver(signals.progress_considered_complete)
def send_student_challenge_share_encouragement(sender, progress, **kwargs):
    path = reverse('challenges:examples', kwargs={
        "challenge_id": progress.challenge.id
    })
    send(template_name='student-completed-project', to=progress.student, merge_vars={
        "studentname": progress.student.username,
        "challengename": progress.challenge.name,
        "inspiration_url": url_for_template(path)
    })

@receiver(signals.posted_comment)
def send_mentor_progress_update_notice(sender, comment, **kwargs):
    progress = comment.challenge_progress

    if not progress.mentor:
        return

    if sender.profile.is_student:
        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": sender.username,
            "stage": Stage(comment.stage).name
        })
        send(template_name='mentor-student-responded-to-feedback', to=progress.mentor, merge_vars={
            "studentname": sender.username,
            "progress_url": url_for_template(path)
        })

@receiver(signals.posted_comment)
def send_student_mentor_response_notice(sender, comment, **kwargs):
    progress = comment.challenge_progress

    if sender.profile.is_mentor:
        deliver_email('mentor_responded', progress.student.profile, progress=progress, mentor=progress.mentor.profile)

@receiver(signals.approved_training_task)
def send_training_task_approval_notice(sender, user, task, **kwargs):
    if task.completion_email_template:
        send(template_name=task.completion_email_template, to=user)

@receiver(signals.completed_training)
def send_training_completion_notice(sender, approver, **kwargs):
    send(template_name='mentor-account-approved', to=sender)