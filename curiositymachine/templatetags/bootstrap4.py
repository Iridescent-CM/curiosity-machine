from django import template

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/form_group.html')
def form_group(field, **kwargs):
    return {
        "field": field,
    }

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/form_check.html')
def form_check(field, **kwargs):
    return {
        "field": field,
    }

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/form_errors.html')
def form_errors(form, **kwargs):
    return {
        "errors": form.non_field_errors,
    }
