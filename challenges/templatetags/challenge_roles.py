from django import template

register = template.Library()

@register.simple_tag
def can_start_challenges(user):
    return user.is_authenticated and (user.extra.is_student or user.extra.is_family)

@register.simple_tag
def can_see_resources(user):
    return user.is_authenticated and not (user.extra.is_student or user.extra.is_family)
