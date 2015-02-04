from django import template
from challenges.models import Theme

register = template.Library()

from challenges.models import Challenge

@register.filter
def theme_id_from_name(name):
	return Theme.objects.get(name=name).id