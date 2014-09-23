from django.template import Variable, VariableDoesNotExist
from django import template
register = template.Library()

@register.assignment_tag()
def resolve(lookup, target):
    try:
        return lookup[target]
    except IndexError:
        return None