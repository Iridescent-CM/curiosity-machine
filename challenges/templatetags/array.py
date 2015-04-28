from django import template

register = template.Library()

@register.filter
def element_by_index(array_or_dict, index):
    return array_or_dict[index]