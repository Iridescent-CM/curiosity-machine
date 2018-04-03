from challenges.models import Stage
from django import template
from django.urls import reverse
from urllib.parse import urlunparse

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/cm_notifications/notification.html')
def cm_notification(n, **kwargs):
    context = {}

    if n.verb == 'posted':
        commenter = n.actor
        comment = n.action_object
        progress = n.target

        context["text"] = "%s commented on %s" % (commenter, progress.challenge.name)
        if commenter == progress.owner:
            context["stage"] = Stage(comment.stage).name
        path = reverse("educators:conversation", kwargs={
            "student_id": progress.owner.id,
            "challenge_id": progress.challenge.id
        })
        fragment = "comment-%s" % comment.id
    elif n.verb == 'completed':
        completer = n.actor
        progress = n.action_object
        context["text"] = "%s completed %s" % (completer, progress.challenge.name)
        path = reverse("educators:conversation", kwargs={
            "student_id": progress.owner.id,
            "challenge_id": progress.challenge.id
        })
        fragment = "content"

    query = ""
    if n.data and "membership_id" in n.data:
        query = "m=%d" % n.data['membership_id']

    context.update({
        "indicator_class": "indicator-unread" if n.unread else "indicator-read",
        "url": urlunparse(('', '', path, '', query, fragment)),
        "timesince": n.timesince,
    })
    return context
