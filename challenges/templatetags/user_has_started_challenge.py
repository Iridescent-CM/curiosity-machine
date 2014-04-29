from django import template

register = template.Library()

@register.filter
def user_has_started_challenge(user, challenge):
    return user.progresses.filter(challenge=challenge).exists()
