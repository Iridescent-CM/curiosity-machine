from django import template

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/form_group.html')
def form_group(field, **kwargs):
    context = {
        "field": field,
        "field_class": "form-control",
        "help_text_classes": kwargs.get("help_text_classes", "text-muted")
    }
    context.update(kwargs)
    return context

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/email_form_group.html')
def email_form_group(field, email=None, **kwargs):
    context = {
        "field": field,
        "email": email,
    }
    context.update(kwargs)
    return context

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
