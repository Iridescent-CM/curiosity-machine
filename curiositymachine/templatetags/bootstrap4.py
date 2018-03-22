from django import template

register = template.Library()

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/form_group.html', takes_context=True)
def form_group(context, field, **kwargs):
    tagcontext = {
        "field": field,
        "field_class": "form-control",
        "form_group_style": kwargs.get("group_style", ""),
        "help_text_classes": kwargs.get("help_text_classes", "text-muted"),
        "required": field.field.required or kwargs.get('required', False),
        "show_required": context.get("SHOW_REQUIRED", False),
    }
    tagcontext.update(kwargs)
    return tagcontext

@register.inclusion_tag('curiositymachine/templatetags/bootstrap4/email_form_group.html', takes_context=True)
def email_form_group(context, field, email=None, **kwargs):
    tagcontext = {
        "field": field,
        "email": email,
        "required": field.field.required,
        "show_required": context.get("SHOW_REQUIRED", False),
    }
    tagcontext.update(kwargs)
    return tagcontext

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
