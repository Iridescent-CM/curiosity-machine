from django import template
from django.urls import reverse
from urllib.parse import urlunparse

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/cm_notifications/notification.html')
def cm_notification(n, **kwargs):
    if n.verb == 'posted':
        text = "%s commented on %s" % (n.actor, n.target.challenge.name)
        path = reverse("educators:conversation", kwargs={
            "student_id": n.target.owner.id,
            "challenge_id": n.target.challenge.id
        })
        fragment = "comment-%s" % n.action_object.id
    elif n.verb == 'completed':
        text = "%s %s %s" % (n.actor, n.verb, n.action_object.challenge.name)
        path = reverse("educators:conversation", kwargs={
            "student_id": n.action_object.owner.id,
            "challenge_id": n.action_object.challenge.id
        })
        fragment = "content"

    query = ""
    if "membership_id" in n.data:
        query = "m=%d" % n.data['membership_id']


    context = {
        "indicator_class": "indicator-unread" if n.unread else "indicator-read",
        "url": urlunparse(('', '', path, '', query, fragment)),
        "text": text,
        "timesince": n.timesince,
    }
    return context
