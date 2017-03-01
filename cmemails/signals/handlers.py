from curiositymachine import signals
from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from cmemails import send, subscribe
from cmemails.mandrill import url_for_template
from challenges.models import Stage
import urllib.parse
import re

@receiver(signals.created_account)
def send_welcome_email(sender, **kwargs):
    if sender.profile.send_welcome and not getattr(sender, "skip_welcome_email", False):
        if sender.profile.is_student:
            template = 'student-u13-welcome' if sender.profile.is_underage() else 'student-welcome'
            send(template_name=template, to=sender, merge_vars={
                'studentname': sender.username
            })
        elif sender.profile.is_educator:
            send(template_name='educator-welcome', to=sender, merge_vars={
                'username': sender.username
            })
        elif sender.profile.is_parent:
            send(template_name='parent-welcome', to=sender, merge_vars={
                'username': sender.username
            })

    if not getattr(sender, "skip_mailing_list_subscription", False):
        subscribe(sender)

@receiver(signals.underage_activation_confirmed)
def send_activation_confirmation(sender, account, **kwargs):
    send(template_name='student-u13-account-activated', to=account, merge_vars={
        'studentname': account.username
    })

@receiver(signals.started_first_project)
def send_first_project_encouragement(sender, progress, **kwargs):
    send(template_name='student-submitted-first-project', to=sender, merge_vars={
        'studentname': sender.username
    })

@receiver(signals.inspiration_gallery_submission_created)
def send_example_submission_notice(sender, example, **kwargs):
    send(template_name='student-submitted-example', to=sender, merge_vars={
        'challengename': example.challenge.name,
        'challenges_url': url_for_template(reverse('challenges:challenges'))
    })

@receiver(signals.inspiration_gallery_submissions_rejected)
def send_example_rejection_notices(sender, queryset, **kwargs):
    for example in queryset.all():
        path = reverse("challenges:examples", kwargs={ "challenge_id": example.challenge.id })
        send(template_name='student-example-declined', to=example.progress.student, merge_vars={
            'challengename': example.challenge.name,
            'inspiration_url': url_for_template(path),
        })

@receiver(signals.inspiration_gallery_submissions_approved)
def send_example_approval_notices(sender, queryset, **kwargs):
    for example in queryset.all():
        path = reverse("challenges:examples", kwargs={ "challenge_id": example.challenge.id })
        send(template_name='student-example-approved', to=example.progress.student, merge_vars={
            'challengename': example.challenge.name,
            'inspiration_url': url_for_template(path)
        })

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
        path = reverse('challenges:challenge_progress', kwargs={
            "challenge_id": progress.challenge.id,
            "username": progress.student.username,
            "stage": Stage(comment.stage).name
        })
        send(template_name='student-mentor-feedback', to=progress.student, merge_vars={
            "studentname": progress.student.username,
            "button_url": url_for_template(path)
        })

@receiver(signals.completed_training)
def send_training_completion_notice(sender, approver, **kwargs):
    send(template_name='mentor-account-approved', to=sender)

@receiver(signals.student_password_changed)
def send_student_password_change_notice(sender, student, resetter, **kwargs):
    send(template_name='student-password-reset-in-membership', to=student, merge_vars={
        'studentname': student.username
    })
