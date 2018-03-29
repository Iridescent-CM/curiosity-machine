from challenges.models import Stage
from django import template
from django.urls import reverse
from urllib.parse import urlunparse

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/cm_notifications/notification.html')
def cm_notification(n, **kwargs):
    context = {}

    if n.verb == 'posted':
        context["text"] = "%s commented on %s" % (n.actor, n.target.challenge.name)
        context["stage"] = Stage(n.action_object.stage).name
        path = reverse("educators:conversation", kwargs={
            "student_id": n.target.owner.id,
            "challenge_id": n.target.challenge.id
        })
        fragment = "comment-%s" % n.action_object.id
    elif n.verb == 'completed':
        context["text"] = "%s %s %s" % (n.actor, n.verb, n.action_object.challenge.name)
        path = reverse("educators:conversation", kwargs={
            "student_id": n.action_object.owner.id,
            "challenge_id": n.action_object.challenge.id
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
