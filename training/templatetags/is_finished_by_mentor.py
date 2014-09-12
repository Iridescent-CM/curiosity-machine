from django import template

register = template.Library()

@register.filter
def is_finished_by_mentor(task, mentor):
	return task.is_finished_by_mentor(mentor)