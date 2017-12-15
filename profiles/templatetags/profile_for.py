from django import template
from profiles.models import User

register = template.Library()

@register.simple_tag
def profile_for(user):
    return User.profile_for(user)
