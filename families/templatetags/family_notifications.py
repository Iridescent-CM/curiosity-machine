from challenges.models import Stage
from django import template
from django.urls import reverse
from urllib.parse import urlunparse

register = template.Library()

@register.inclusion_tag('families/templatetags/family_notifications/notification.html')
def family_notification(n, **kwargs):
    context = {}

    commenter = n.actor
    comment = n.action_object
    progress = n.target

    context["text"] = "%s commented on %s" % (commenter, progress.challenge.name)
    if commenter == progress.owner:
        context["stage"] = Stage(comment.stage).name
    path = reverse("challenges:challenge_progress", kwargs={
        "username": progress.owner.username,
        "challenge_id": progress.challenge.id
    })

    context.update({
        "indicator_class": "indicator-unread" if n.unread else "indicator-read",
        "url": urlunparse(('', '', path, '', '', '')),
        "timesince": n.timesince,
    })
    return context
