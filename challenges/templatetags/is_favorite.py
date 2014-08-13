from django import template

register = template.Library()

from challenges.models import Challenge

@register.filter
def is_favorite(challenge, user):
	return challenge.is_favorite(user)