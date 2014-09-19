from django import template

register = template.Library()

@register.filter
def is_greater_length(subject, length):
	return len(subject) > length