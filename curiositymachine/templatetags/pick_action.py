from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def pick_action(form, **kwargs):
    edit_viewname = kwargs.pop('edit')
    create_viewname = kwargs.pop('create')
    if form.instance and form.instance.pk:
        viewname = edit_viewname
    else:
        viewname = create_viewname
    return reverse(viewname, **kwargs)
