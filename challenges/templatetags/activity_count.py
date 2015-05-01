from django import template
from challenges.models import Stage

register = template.Library()

@register.simple_tag
def activity_count(progress, user=None, *stages):
    filters = {}
    if user:
        filters['user'] = user
    if stages:
        filters['stage__in'] = [Stage[stage].value for stage in stages]
    return progress.comments.filter(**filters).count()
