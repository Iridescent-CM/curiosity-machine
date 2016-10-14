from django.core.exceptions import ValidationError
import re

def validate_has_non_numeric(value):
    regex = r"\D"
    if not re.search(regex, value):
        raise ValidationError("Must contain at least one non-numeric character", code="invalid")
