from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def ifactive(context, viewname, classname):
    rm = context['request'].resolver_match
    current = "%s:%s" % (rm.app_name, rm.url_name)
    if viewname == current:
        return classname
    return ''
