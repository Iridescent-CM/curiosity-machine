from django import template
from django.utils.timezone import now

register = template.Library()

@register.inclusion_tag('curiositymachine/datepill.html')
def datepill(dt, now=now()):
    days = (now.date() - dt.date()).days
    text = ""
    if days <= 0:
        text = "Today"
    elif days == 1:
        text = "1 day"
    elif days < 7:
        text = str(days) + " days"
    elif days < 14:
        text = "1 week"
    elif days < 30:
        text = "2 weeks"
    else:
        text = "1+ month"

    color = "default"
    if days < 5:
        color = "success"
    elif days < 14:
        color = "warning"

    return {
        'text': text,
        'color': color
    }