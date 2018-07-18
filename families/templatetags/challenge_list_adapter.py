from django import template

register = template.Library()

@register.assignment_tag
def adapt_to_challenge(obj):
    if not hasattr(obj, "image"):
        obj.image = obj.card_image
    if not hasattr(obj, "name"):
        obj.name = obj.title
    return obj
