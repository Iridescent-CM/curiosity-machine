from curiositymachine import signals
from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from cmemails import send, subscribe
from cmemails.mandrill import url_for_template
from challenges.models import Stage
import urllib.parse
import re

@receiver(signals.created_profile)
def send_welcome_email(sender, **kwargs):
    if sender.extra.send_welcome and not getattr(sender, "skip_welcome_email", False):
        if sender.extra.is_student:
            if sender.studentprofile.is_underage():
                pass # handled through hellosign
            else:
                send(template_name='student-welcome', to=sender, merge_vars={
                    'studentname': sender.username
                })
        elif sender.extra.is_educator:
            send(template_name='educator-welcome', to=sender, merge_vars={
                'username': sender.username
            })
        elif sender.extra.is_parent:
            send(template_name='parent-welcome', to=sender, merge_vars={
                'username': sender.username
            })

    if not getattr(sender, "skip_mailing_list_subscription", False):
        subscribe(sender)

@receiver(signals.account_activation_confirmed)
def send_activation_confirmation(sender, **kwargs):
    if sender.extra.is_family:
        send(template_name='family-account-account-activated', to=sender, merge_vars={
            'username': sender.username
        })

@receiver(signals.underage_activation_confirmed)
def send_underage_activation_confirmation(sender, **kwargs):
    send(template_name='student-u13-account-activated', to=sender, merge_vars={
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
        send(template_name='student-example-declined', to=example.progress.owner, merge_vars={
            'challengename': example.challenge.name,
            'inspiration_url': url_for_template(path),
        })

@receiver(signals.inspiration_gallery_submissions_approved)
def send_example_approval_notices(sender, queryset, **kwargs):
    for example in queryset.all():
        path = reverse("challenges:examples", kwargs={ "challenge_id": example.challenge.id })
        send(template_name='student-example-approved', to=example.progress.owner, merge_vars={
            'challengename': example.challenge.name,
            'inspiration_url': url_for_template(path)
        })

@receiver(signals.completed_training)
def send_training_completion_notice(sender, **kwargs):
    send(template_name='mentor-account-approved', to=sender, merge_vars={
        "username": sender.username
    })

@receiver(signals.member_password_changed)
def send_member_password_change_notice(sender, member, resetter, **kwargs):
    if member.extra.is_student:
        send(template_name='student-password-reset-in-membership', to=member, merge_vars={
            'studentname': member.username
        })
    elif member.extra.is_family:
        send(template_name='family-account-password-changed', to=member, merge_vars={
            'username': member.username
        })
