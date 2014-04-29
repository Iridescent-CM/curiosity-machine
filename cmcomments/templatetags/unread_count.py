from django import template

register = template.Library()

from challenges.models import Progress

@register.filter
def unread_count(progress, user):
    if progress is None or user is None:
        return None
    return len(progress.get_unread_comments_for_user(user))
